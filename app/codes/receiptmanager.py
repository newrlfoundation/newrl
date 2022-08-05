"""Receipt manager"""

import sqlite3

from app.codes.fs.temp_manager import get_all_receipts_from_storage, remove_receipt_from_temp
from .statereader import get_public_key_from_wallet_address
from ..constants import NEWRL_DB



def get_receipts_included_in_block_from_db(block_index):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    receipt_cursor = cur.execute(
        'SELECT * FROM receipts where included_block_index=?', (block_index,))
    
    _receipts = receipt_cursor.fetchall()
    receipts = []
    for _receipt in _receipts:
        receipt_data = {
            'block_index': _receipt['block_index'],
            'block_hash':_receipt['block_hash'],
            'vote': _receipt['vote'],
            'timestamp': _receipt['timestamp'],
            "wallet_address": _receipt['wallet_address'],
        }
        wallet_public = get_public_key_from_wallet_address(_receipt['wallet_address'], con)
        receipt = {
            "data": receipt_data,
            "public_key": wallet_public,
            "signature": _receipt['signature'],
        }
        receipts.append(receipt)

    return receipts


def update_receipts_in_state(cur, block):
    if 'previous_block_receipts' not in block['text']:
        return
    receipts = block['text']['previous_block_receipts']

    for receipt in receipts:
        db_receipt_data = (
            receipt['data']['block_index'],
            receipt['data']['block_hash'],
            receipt['data']['vote'],
            receipt['data']['wallet_address'],
            # wallet_address,
            block['index'],
            receipt['signature'],
            receipt['data']['timestamp'],
        )

        cur.execute('''
            INSERT OR IGNORE INTO receipts 
            (block_index, block_hash, vote, wallet_address, 
            included_block_index, signature, timestamp)
            VALUES(?, ?, ?, ?, ?, ?, ?)
        ''', db_receipt_data)

        remove_receipt_from_temp(
            receipt['data']['block_index'],
            receipt['data']['block_hash'],
            receipt['data']['wallet_address'])


def check_receipt_exists_in_db(block_index, block_hash, wallet_address, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        connection_created = True
    else:
        connection_created = False

    receipt_cursor = cur.execute(
        '''
        SELECT vote FROM receipts where block_index=? and block_hash=? and wallet_address=?
        '''
        , (block_index, block_hash, wallet_address)).fetchone()
    
    receipt_exists = receipt_cursor is not None
    if connection_created:
        con.close()
    return receipt_exists


def get_receipt_in_temp_not_in_chain(exclude_block, cur=None):
    receipts = get_all_receipts_from_storage(exclude_block_index=exclude_block)
    receipts_not_included = []
    for receipt in receipts:
        if check_receipt_exists_in_db(
            receipt['data']['block_index'],
            receipt['data']['block_hash'],
            receipt['data']['wallet_address'],
            ):
            remove_receipt_from_temp(
                receipt['data']['block_index'],
                receipt['data']['block_hash'],
                receipt['data']['wallet_address'],
            )
        else:
            receipts_not_included.append(receipt)
    
    return receipts_not_included