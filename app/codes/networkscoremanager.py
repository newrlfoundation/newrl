"""Helper functions for network trust score updates"""
import logging
import json
from math import sqrt

from app.Configuration import Configuration
from app.codes.clock.global_time import get_corrected_time_ms
from app.codes.db_updater import get_block_from_cursor, get_pid_from_wallet, update_trust_score
from app.codes.state_updater import slashing_tokens

from app.constants import INITIAL_NETWORK_TRUST_SCORE, MAX_NETWORK_TRUST_SCORE
from app.ntypes import BLOCK_STATUS_INVALID_MINED, BLOCK_VOTE_MINER, BLOCK_VOTE_VALID



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_valid_block_creation_score(current_score):
    score_diff = sqrt(MAX_NETWORK_TRUST_SCORE - current_score)/2
    new_score = int(current_score + score_diff)
    return new_score


def get_invalid_block_creation_score(current_score):
    score_diff = 5 * (MAX_NETWORK_TRUST_SCORE/100 + 0.01 * current_score)
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
    try:
        committee = json.loads(block['committee'])
        return committee
    except Exception as e:
        logger.info(f'Committee not available in block {block["block_index"]}')
        return []


def update_network_trust_score_from_receipt(cur, receipt):
        wallet_address = receipt['data']['wallet_address']
        person_id = get_pid_from_wallet(cur, wallet_address)
        vote = receipt['data']['vote']
        receipt_timestamp = receipt['data']['timestamp']

        trust_score_cursor = cur.execute('''
            SELECT score FROM trust_scores where src_person_id=? and dest_person_id=?
            ''', (Configuration.config("NETWORK_TRUST_MANAGER_PID"), person_id)).fetchone()
                    
        if trust_score_cursor is None:
            existing_score = INITIAL_NETWORK_TRUST_SCORE
        else:
            existing_score = trust_score_cursor[0]

        target_block_index = receipt['data']['block_index']
        target_block_hash = receipt['data']['block_hash']
        actual_block = get_block_from_cursor(cur, target_block_index)
        if actual_block is None:
            return
        actual_block_hash = actual_block['hash']
        if vote == BLOCK_VOTE_MINER:
            if actual_block['proof'] == 42:  # Empty block check
                if actual_block['status'] == 2:
                    score = get_invalid_block_creation_score(existing_score)
                else:
                    score = existing_score
            else:
                if actual_block['creator_wallet'] == wallet_address:
                    if actual_block_hash == target_block_hash:
                        score = get_valid_block_creation_score(existing_score)
                    else:
                        score = get_invalid_block_creation_score(existing_score)
                        logger.info('Actual block hash is not matching proposed block for %d. Slashing proposer %s',
                            actual_block['index'], wallet_address)
                        slashing_tokens(cur, wallet_address, True)
                else:
                    score = get_invalid_block_creation_score(existing_score)
                    logger.info('Block proposer is not matching creator_wallet for block %d. Slashing proposer %s',
                            actual_block['index'], wallet_address)
                    slashing_tokens(cur, wallet_address, True)
        else:
            committee = get_committee_for_block(actual_block)
            if actual_block['proof'] == 42:  # Empty block check
                if actual_block['status'] == BLOCK_STATUS_INVALID_MINED:
                    if vote == BLOCK_VOTE_VALID:
                        score = get_invalid_receipt_score(existing_score)
                        logger.info('Committee member voted positive for invalid block %d. Slashing voter %s',
                            actual_block['index'], wallet_address)
                        slashing_tokens(cur, wallet_address, False)

                    else:
                        score = get_valid_receipt_score(existing_score)
                else:
                    score = existing_score
            else:
                if actual_block_hash != target_block_hash:
                    score = existing_score
                else:
                    if vote == BLOCK_VOTE_VALID:
                        score = get_valid_receipt_score(existing_score)
                    else:
                        score = get_invalid_receipt_score(existing_score)
                        logger.info('Committee member voted negative for valid block %d. Slashing voter %s',
                            actual_block['index'], wallet_address)
                        slashing_tokens(cur, wallet_address, False)
            if wallet_address not in committee:
                score = get_invalid_receipt_score(existing_score)
                slashing_tokens(cur, wallet_address, False)
                logger.info('Non-committee member voted for block %d. Slashing voter %s',
                            actual_block['index'], wallet_address)


        update_trust_score(cur, Configuration.config("NETWORK_TRUST_MANAGER_PID"), person_id, score, receipt_timestamp)