"""Temp file manager"""

import glob
import json
import os

from app.config.constants import MEMPOOL_PATH, MEMPOOL_TRANSACTION_LIFETIME_SECONDS, TMP_PATH
from ..clock.global_time import get_corrected_time_ms

def get_receipts_from_storage(block_index, folder=TMP_PATH):
    """Returns a list of receipts matching a block index from mempool"""
    blocks = []
    for block_file in glob.glob(f'{folder}/receipt_{block_index}_*.json'):
        with open(block_file, 'r') as _file:
            block = json.load(_file)
            blocks.append(block)
    return blocks


# def store_receipt_to_temp(receipt, folder=TMP_PATH):
#     block_index = receipt['data']['block_index']
#     existing_files_for_block = glob.glob(f'{folder}/receipt_{block_index}_*.json')
#     new_file_name = f'{folder}/receipt_{block_index}_{len(existing_files_for_block)}.json'
#     with open(new_file_name, 'w') as _file:
#         json.dump(receipt, _file)
#     return new_file_name


def append_receipt_to_block(block, new_receipt):
    if 'receipts' not in block:
        block['receipts'] = []
    
    receipt_already_exists = False
    for receipt in block['receipts']:
        if receipt['public_key'] == new_receipt['public_key']:
            receipt_already_exists = True
            break
    
    if not receipt_already_exists:
        block['receipts'].append(new_receipt)
        return True
    
    return False


def transaction_exists_in_mempool(transaction_code):
    existing_files_for_block = glob.glob(f'{MEMPOOL_PATH}transaction-*-{transaction_code}*.json')
    if len(existing_files_for_block) == 0:
        return False
    return True


def get_mempool_transaction(transaction_code):
    existing_files_for_block = glob.glob(f'{MEMPOOL_PATH}transaction-*-{transaction_code}*.json')
    if len(existing_files_for_block) == 0:
        return None
    
    with open(existing_files_for_block[0], 'r') as _file:
        transaction = json.load(_file)
        return transaction


def remove_transaction_from_mempool(transaction_code):
    transaction_files = glob.glob(f'{MEMPOOL_PATH}transaction-*-{transaction_code}*.json')
    for f in transaction_files:
        os.remove(f)


def clear_mempool():
    filenames = os.listdir(MEMPOOL_PATH)
    
    for filename in filenames:
        file = MEMPOOL_PATH + filename
        os.remove(file)
    
    clear_temp()

def clear_temp():
    filenames = glob.glob(f'{TMP_PATH}*.json')
    print(filenames)
    
    for f in filenames:
        os.remove(f)


def mempool_cleanup():
    transaction_files = glob.glob(f'{MEMPOOL_PATH}transaction-*.json')

    for transaction_file in transaction_files:
        with open(transaction_file, 'r') as _file:
            t = json.load(_file)
            if t['transaction']['timestamp'] < get_corrected_time_ms() - MEMPOOL_TRANSACTION_LIFETIME_SECONDS * 1000:
                os.remove(transaction_file)
