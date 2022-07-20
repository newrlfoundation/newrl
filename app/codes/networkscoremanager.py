"""Helper functions for network trust score updates"""
from math import sqrt
from app.codes.clock.global_time import get_corrected_time_ms
from app.codes.db_updater import get_block_from_cursor, get_pid_from_wallet, update_trust_score
from app.codes.state_updater import slashing_tokens

from app.constants import INITIAL_NETWORK_TRUST_SCORE, MAX_NETWORK_TRUST_SCORE
from app.ntypes import BLOCK_VOTE_MINER, BLOCK_VOTE_VALID
from app.nvalues import NETWORK_TRUST_MANAGER_PID


def get_valid_block_creation_score(current_score):
    score_diff = sqrt(MAX_NETWORK_TRUST_SCORE - current_score)/2
    new_score = int(current_score + score_diff)
    return new_score


def get_invalid_block_creation_score(current_score):
    score_diff = 5 * MAX_NETWORK_TRUST_SCORE/100 + 0.01 * current_score
    new_score = int(current_score - score_diff)
    return new_score


def get_valid_receipt_score(current_score):
    score_diff = sqrt(MAX_NETWORK_TRUST_SCORE - current_score) / 20
    new_score = int(current_score + score_diff)
    return new_score


def get_invalid_receipt_score(current_score):
    score_diff = 0.5 * (MAX_NETWORK_TRUST_SCORE/100 + 0.01 * current_score)
    new_score = int(current_score - score_diff)
    return new_score


def get_committee_for_block(block):
    return [block['creator_wallet']]


def update_network_trust_score_from_receipt(cur, receipt):
    wallet_cursor = cur.execute(
        'SELECT wallet_address FROM wallets where wallet_public=?', 
        (receipt['public_key'],)).fetchone()
    
    if wallet_cursor is not None:
        wallet_address = wallet_cursor[0]
        person_id = get_pid_from_wallet(cur, wallet_address)
        vote = receipt['data']['vote']

        trust_score_cursor = cur.execute('''
            SELECT score FROM trust_scores where src_person_id=? and dest_person_id=?
            ''', (NETWORK_TRUST_MANAGER_PID, person_id)).fetchone()
                    
        if trust_score_cursor is None:
            existing_score = INITIAL_NETWORK_TRUST_SCORE
        else:
            existing_score = trust_score_cursor[0]

        target_block_index = receipt['data']['block_index']
        target_block_hash = receipt['data']['block_hash']
        actual_block = get_block_from_cursor(cur, target_block_index)
        actual_block_hash = actual_block['hash']
        if vote == BLOCK_VOTE_MINER:
            # Miner vote
            if actual_block['creator_wallet'] == wallet_address:
                if actual_block_hash == target_block_hash:
                    score = get_valid_block_creation_score(existing_score)
                    slashing_tokens(cur,wallet_address,True)
                else:
                    if actual_block['proof'] == 42:  # Empty block check
                        score = existing_score
                    else:
                        score = get_invalid_block_creation_score(existing_score)
                        slashing_tokens(cur, wallet_address, True)
            else:
                score = get_invalid_block_creation_score(existing_score)
                slashing_tokens(cur, wallet_address, True)
        else:
            # Committee member vote
            committee = get_committee_for_block(actual_block)
            if wallet_address not in committee:
                score = get_invalid_receipt_score(existing_score)
                slashing_tokens(cur, wallet_address, False)
            else:
                if actual_block_hash != target_block_hash:
                    if actual_block['proof'] != 42:  # Empty block check
                        score = get_invalid_receipt_score(existing_score)
                        slashing_tokens(cur, wallet_address, False)
                    else:
                        score = existing_score
                else:
                    if vote == BLOCK_VOTE_VALID:
                        score = get_valid_receipt_score(existing_score)
                    else:
                        score = get_invalid_receipt_score(existing_score)
                        slashing_tokens(cur, wallet_address, False)

        update_trust_score(cur, NETWORK_TRUST_MANAGER_PID, person_id, score, get_corrected_time_ms())