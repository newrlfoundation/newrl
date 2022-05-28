"""Python programm to validate transactions, blocks and receipts"""

import base64
import datetime
import json
import logging

import ecdsa
import os

from app.codes.fs.mempool_manager import get_mempool_transaction
from app.codes.p2p.transport import send
from .utils import get_last_block_hash
from .transactionmanager import Transactionmanager
from ..constants import IS_TEST, MEMPOOL_PATH
from .p2p.outgoing import propogate_transaction_to_peers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(transaction, propagate=False, validate_economics=True):
    existing_transaction = get_mempool_transaction(transaction['transaction']['trans_code'])
    if existing_transaction is not None:
        return {'valid': True, 'msg': 'Already validated and in mempool'}

    transaction_manager = Transactionmanager()
    transaction_manager.set_transaction_data(transaction)
    signatures_valid = transaction_manager.verifytransigns()
    valid = False
    if not signatures_valid:
        msg = "Transaction has invalid signatures"
    if validate_economics:
        economics_valid = transaction_manager.econvalidator()
        if not economics_valid:
            msg = "Transaction economic validation failed"
            valid = False
        msg = "Transaction economic validation successful"
        valid = True
    else:
        msg = "Valid signatures. Not checking economics"
        valid = True
    # if  economics_valid and signatures_valid:
    #     msg = "Transaction is valid"
    #     valid = True
    # if not economics_valid:
    #     msg = "Transaction economic validation failed"
    
    check = {'valid': valid, 'msg': msg}

    if valid:  # Economics and signatures are both valid
        transaction_file = f"{MEMPOOL_PATH}transaction-{transaction_manager.transaction['type']}-{transaction_manager.transaction['trans_code']}.json"
        transaction_manager.save_transaction_to_mempool(transaction_file)

        if propagate and not IS_TEST:
            # Broadcast transaction to peers via HTTP
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
    public_key_bytes = base64.b64decode(public_key)
    sign_trans_bytes = base64.decodebytes(signature.encode('utf-8'))
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


def validate_block_receipts(block):
    total_receipt_count = 0
    positive_receipt_count = 0
    for receipt in block['receipts']:
        total_receipt_count += 1

        if not validate_receipt_signature(receipt):
            continue

        if receipt['data']['block_index'] != block['index'] or receipt['data']['vote'] < 1:
            continue

        trust_score = get_node_trust_score(receipt['public_key'])
        valid_probability = 0 if trust_score < 0 else (trust_score + 2) / 5

        if receipt['data']['vote'] == 1:
            positive_receipt_count += 1
    
    return {
        'total_receipt_count': total_receipt_count,
        'positive_receipt_count': positive_receipt_count,
    }


def validate_block(block):
    if not validate_block_data(block['data']):
        return False

    return True


def validate_block_data(block):
    last_block = get_last_block_hash()

    if not last_block:
        # No local chain. Sync anyway.
        return True

    if last_block['hash'] != block['previous_hash']:
        print('Previous block hash does not match latest block')
        return False
    
    block_index = block['block_index'] if 'block_index' in block else block['index']
    if last_block['index'] != block_index - 1:
        print('New block index is not 1 more than last block index')
        return False
    return True


def validate_block_transactions(block):
    for transaction in block['text']['transactions']:
        validation_result = validate(transaction, propagate=False, validate_economics=True)
        if not validation_result['valid']:
            return False
    return True
