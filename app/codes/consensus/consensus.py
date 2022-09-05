"""Consensus related functions"""

import logging

from app.codes.committeemanager import get_committee_wallet_list_for_current_block

from ..receiptmanager import validate_receipt
from ..kycwallet import get_address_from_public_key
from ...ntypes import BLOCK_VOTE_INVALID, BLOCK_VOTE_MINER, BLOCK_VOTE_VALID
from ...nvalues import SENTINEL_NODE_WALLET
from ..clock.global_time import get_corrected_time_ms
from ..signmanager import sign_object, verify_sign
from ..blockchain import calculate_hash, get_last_block
from ..validator import count_block_receipts
from ...Configuration import Configuration
from ..fs.mempool_manager import append_receipt_to_block, get_receipts_from_storage
from ...constants import BLOCK_RECEIVE_TIMEOUT_SECONDS, BLOCK_TIME_INTERVAL_SECONDS, COMMITTEE_SIZE, MINIMUM_ACCEPTANCE_RATIO, MINIMUM_ACCEPTANCE_VOTES, NO_BLOCK_TIMEOUT
from ..auth.auth import get_wallet
from ..minermanager import get_committee_for_current_block, get_miner_for_current_block

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    wallet_data = get_wallet()
except:
    wallet_data = {
        'wallet': {'public': '', 'private': ''},
    }
wallet_address = wallet_data['address']
public_key = wallet_data['public']
private_key = wallet_data['private']


def generate_block_receipt(block, vote=BLOCK_VOTE_VALID):
    receipt_data = {
        'block_index': block['index'],
        'block_hash': calculate_hash(block),
        'vote': vote,
        'timestamp': get_corrected_time_ms(),
        "wallet_address": wallet_address,
    }
    return {
        "data": receipt_data,
        "public_key": public_key,
        "signature": sign_object(private_key, receipt_data),
    }


def add_my_receipt_to_block(block, vote=BLOCK_VOTE_VALID):
    """Add node's receipt to the block. Return receipt if receipt added. None if receipt already present."""
    my_receipt = generate_block_receipt(block['data'], vote)
    my_receipt_already_added = False
    for receipt in block['receipts']:
        if receipt['public_key'] == my_receipt['public_key']:
            my_receipt_already_added = True
    if not my_receipt_already_added:
        block['receipts'].append(my_receipt)
        return my_receipt
    return None


def get_node_trust_score(public_key):
    # TODO - Return the actual trust score of the node by lookup on public_key
    return 1

# Probability version
# def check_community_consensus(block):
#     total_receipt_count = 0
#     score_weighted_validity_count = 0

#     for receipt in block['receipts']:
#         total_receipt_count += 1

#         trust_score = get_node_trust_score(receipt['public_key'])
#         valid_probability = 0 if trust_score < 0 else (trust_score + 2) / 5

#         score_weighted_validity_count += valid_probability

#     if score_weighted_validity_count < 0.75:
#         return False
    
#     return True


def get_committee_consensus(block):
    """
    Check a block for consensus
    Return -1 for invalid block conensus
    Return 1 for valid block conensus
    Return 0 for no conensus
    """
    receipts_in_temp = get_receipts_from_storage(block['index'])

    for receipt in receipts_in_temp:
        append_receipt_to_block(block, receipt)

    receipt_counts = count_block_receipts(block)
    committee = block['data']['committee']

    if len(committee) == 1:
        if committee[0] == Configuration.config("SENTINEL_NODE_WALLET"):  # Todo - Check if block is empty
            logger.info('Consensus satisfied as sentinel node is the miner')
            return 1
        else:
            return 0
    if len(committee) < MINIMUM_ACCEPTANCE_VOTES:
        return 0

    if receipt_counts['positive_receipt_count'] + 1 >= MINIMUM_ACCEPTANCE_VOTES:
        # TODO - Check if time elapsed has exceeded receipt cut off. Do not accept otherwise
        # This is to give every node sometime to send their receipts for the block
        return 1
    elif receipt_counts['negative_receipt_count'] >= MINIMUM_ACCEPTANCE_VOTES:
        return -1
    return 0


def validate_block_miner_committee(block):
    creator_wallet = block['data']['creator_wallet']

    expected_miner = get_miner_for_current_block()['wallet_address']

    if expected_miner is None:
        return True

    if creator_wallet != expected_miner:
        logger.info(f"Invalid miner {creator_wallet} for block. Expected {expected_miner}")
        return False
    
    expected_commitee = get_committee_wallet_list_for_current_block()
    if set(block['data']['committee']) != set(expected_commitee):
        logger.info(f"Invalid committee {block['data']['committee']} for block. Expected {expected_commitee}")
        return False
    
    # Signature checks
    # TODO - Check if block hash is being validated anywhere else. If not add it here. 
    miner_vote_found = False
    for receipt in block['receipts']:
        if not validate_receipt(receipt):
            logger.warn('Invalid receipt')
            return False
        validate_receipt_for_committee(receipt, expected_commitee, expected_miner)
        if receipt['data']['vote'] == BLOCK_VOTE_MINER:
            if miner_vote_found:
                logger.warn('Two different miner votes found in receipt')
                return False
            miner_vote_found = True
        
    if not miner_vote_found:
        logger.warn('Miner vote not found in receipts')
        return False
    
    return True


def validate_receipt_for_committee(receipt,
                                   expected_commitee=None,
                                   expected_miner=None):
    if expected_commitee is None:
        expected_commitee = get_committee_wallet_list_for_current_block()
    if expected_miner is None:
        expected_miner = get_miner_for_current_block()['wallet_address']
    signer_address = receipt['data']['wallet_address']
    if receipt['data']['vote'] in [BLOCK_VOTE_VALID, BLOCK_VOTE_INVALID]:
        if signer_address not in expected_commitee:
            logger.warn('Receipt signing wallet not in committee')
            return False
    elif receipt['data']['vote'] == BLOCK_VOTE_MINER:
        if signer_address != expected_miner:
            logger.warn('Miner vote with non-expected miner found in receipts')
            return False
    else:
        logger.warn('Invalid vote in receipt')
        return False
    return True


def validate_empty_block(block, check_sentinel_receipt=False):
    """
    Validate if the block is a timeout block with
        1. No transactions
        2. Proof = 42
        3. timestamp = BLOCK_TIME_INTERVAL_SECONDS + NO_BLOCK_TIMEOUT
    """
    block_data = block['data']

    # Check sentinel node signature
    if check_sentinel_receipt:
        if len(block['receipts']) != 1:
            return False
        
        receipt = block['receipts'][0]
        if not validate_receipt(receipt):
            logger.warn('Invalid receipt')
            return False
        
        if receipt['data']['wallet_address'] != SENTINEL_NODE_WALLET:
            logger.warn('Receipt not from sentinel node')
            return False


    last_block = get_last_block()
    if last_block is None:
        return True
    time_ms_elapsed_since_last_block = get_corrected_time_ms() - int(last_block['timestamp'])
    block_cuttoff_triggered = time_ms_elapsed_since_last_block > (BLOCK_TIME_INTERVAL_SECONDS + BLOCK_RECEIVE_TIMEOUT_SECONDS) * 1000
    expected_empty_block_timestamp = int(last_block['timestamp']) + (BLOCK_TIME_INTERVAL_SECONDS + NO_BLOCK_TIMEOUT) * 1000
    if (block_data['proof'] == 42 
        and len(block_data['text']['transactions']) == 0 and block_cuttoff_triggered
        and block_data['timestamp'] == expected_empty_block_timestamp):
        return True
