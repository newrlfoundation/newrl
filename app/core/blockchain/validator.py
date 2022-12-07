"""Python programm to validate transactions, blocks and receipts"""

import base64
import datetime
import json
import logging

import ecdsa
import os
from app.core.clock.global_time import get_corrected_time_ms
from app.core.crypto.crypto import calculate_hash

from app.core.fs.mempool_manager import transaction_exists_in_mempool
from app.core.p2p.transport import send
from app.config.ntypes import BLOCK_VOTE_INVALID, BLOCK_VOTE_VALID, TRANSACTION_MINER_ADDITION
from ..helpers.utils import get_last_block_hash
from app.core.blockchain.transactionmanager import Transactionmanager
from app.config.constants import IS_TEST, MAX_TRANSACTION_SIZE, MEMPOOL_PATH, MEMPOOL_TRANSACTION_LIFETIME_SECONDS
from ..p2p.outgoing import propogate_transaction_to_peers
from .chainscanner import get_transaction

from jsonschema import validate as jsonvalidate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(transaction, propagate=False, validate_economics=True):
    if not validate_transaction_structure(transaction):
        return {'valid': False, 'msg': 'Invalid transaction structure'}
    # if transaction['transaction']['timestamp'] < get_corrected_time_ms() - MEMPOOL_TRANSACTION_LIFETIME_SECONDS * 1000:
    #     return {
    #         'valid': False,
    #         'msg': 'Transaction is old'
    #     }

    if transaction_exists_in_mempool(transaction['transaction']['trans_code']):
        logger.info('Transaction exists in mempool')
        return {'valid': True, 'msg': 'Already validated and in mempool', 'new_transaction': False}
    
    if get_transaction(transaction['transaction']['trans_code']) is not None:
        logger.info('Transaction exists in state')
        return {'valid': True, 'msg': 'Transaction exists in chain', 'new_transaction': False}

    if transaction['transaction']['type'] != TRANSACTION_MINER_ADDITION and transaction['transaction']['fee'] < 1000000:
        return {'valid': False, 'msg': 'Not enough fee. Min of 1 NWRL is required', 'new_transaction': True}

    if len(json.dumps(transaction)) > MAX_TRANSACTION_SIZE:
        return {'valid': False, 'msg': 'Transaction size exceeded', 'new_transaction': True}
    
    transaction_manager = Transactionmanager()
    transaction_manager.set_transaction_data(transaction)
    signatures_valid = transaction_manager.verifytransigns()
    valid = False
    if not signatures_valid:
        msg = "Transaction has invalid signatures"
    else:
        if validate_economics:
            economics_valid = transaction_manager.econvalidator()
            if not economics_valid:
                msg = "Transaction economic validation failed"
                valid = False
            else:
                msg = "Transaction economic validation successful"
                valid = True
        else:
            msg = "Valid signatures. Not checking economics"
            valid = True
        #contract validation    
        if transaction['transaction']['type'] == 3 and (transaction['transaction']['specific_data']['function']!= "setup"):
            if not transaction_manager.contract_validate():
                msg = "Contract Validation Failed"
                valid = False
    
    check = {'valid': valid, 'msg': msg, 'new_transaction': True}

    if valid:  # Economics and signatures are both valid
        transaction_file = f"{MEMPOOL_PATH}transaction-{transaction_manager.transaction['type']}-{transaction_manager.transaction['trans_code']}.json"
        transaction_manager.save_transaction_to_mempool(transaction_file)

        if propagate and not IS_TEST:
            # Broadcast transaction to peers via HTTP
            if transaction['transaction']['timestamp'] > get_corrected_time_ms() - MEMPOOL_TRANSACTION_LIFETIME_SECONDS * 1000:
                exclude_nodes = transaction['peers_already_broadcasted'] if 'peers_already_broadcasted' in transaction else None
                propogate_transaction_to_peers(
                    transaction_manager.get_transaction_complete(),
                    exclude_nodes=exclude_nodes
                )

            # Broadcaset transaction via transport server
            # try:
            #     payload = {
            #         'operation': 'send_transaction',
            #         'data': transaction_manager.get_transaction_complete()
            #     }
            #     send(payload)
            # except:
            #     print('Error sending transaction to transport server')

    print(msg)
    return check


def validate_signature(data, public_key, signature):
    public_key_bytes = bytes.fromhex(public_key)
    sign_trans_bytes = bytes.fromhex(signature)
    vk = ecdsa.VerifyingKey.from_string(
        public_key_bytes, curve=ecdsa.SECP256k1)
    message = json.dumps(data).encode()
    try:
        return vk.verify(sign_trans_bytes, message)
    except:
        return False


def validate_receipt_signature(receipt):
    try:
        return validate_signature(receipt['data'], receipt['public_key'], receipt['signature'])
    except Exception as e:
        logger.error('Error validating receipt signature')
        return False


def get_node_trust_score(public_key):
    # TODO - Return the actual trust score of the node by lookup on public_key
    return 1


def count_block_receipts(block):
    total_receipt_count = 0
    positive_receipt_count = 0
    negative_receipt_count = 0  # TODO
    for receipt in block['receipts']:
        total_receipt_count += 1

        if receipt['data']['wallet_address'] not in block['data']['committee']:
            continue

        if not validate_receipt_signature(receipt):
            continue

        if receipt['data']['block_index'] != block['index']:
            continue
    
        if receipt['data']['vote'] == BLOCK_VOTE_INVALID:
            negative_receipt_count += 1

        if receipt['data']['vote'] == BLOCK_VOTE_VALID:
            positive_receipt_count += 1
    
    return {
        'total_receipt_count': total_receipt_count,
        'positive_receipt_count': positive_receipt_count,
        'negative_receipt_count': negative_receipt_count
    }


def validate_block(block):
    if not validate_block_data(block['data']):
        return False
    if calculate_hash(block['data']) != block['hash']:
        return False
    # if not validate_block_transactions(block['data']):
    #     return False
    return True


def validate_block_data(block):
    last_block = get_last_block_hash()

    if not last_block:
        # No local chain. Sync anyway.
        return True

    if last_block['hash'] != block['previous_hash']:
        logger.info(f"Previous block hash does not match at index {last_block['index']}. {last_block['hash']} != {block['previous_hash']}")
        return False
    
    block_index = block['block_index'] if 'block_index' in block else block['index']
    if last_block['index'] != block_index - 1:
        logger.info(f"New block index is {block['index']} which is not 1 more than last block index {last_block['index']}")
        return False
    return True


def validate_block_transactions(block):
    for transaction in block['text']['transactions']:
        validation_result = validate(transaction, propagate=False, validate_economics=True)
        if not validation_result['valid']:
            return False
    return True


def validate_transaction_structure(signed_transaction):
    schema = {
        "type": "object",
        "properties": {
            "transaction": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "integer"},
                    "trans_code": {"type": "string"},
                    "type": {"type": "integer"},
                    "currency": {"type": "string"},
                    "fee": {"type": "integer"},
                    "descr": {"type": "string"},
                    "valid": {"type": "integer"},
                    "specific_data": {"type": "object"}
                }
            },
            "signatures": {"type": "array"}
        }
        
    }
    
    jsonvalidate(signed_transaction, schema)

    return True
