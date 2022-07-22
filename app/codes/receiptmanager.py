"""Receipt manager"""

import sqlite3

from app.codes.fs.temp_manager import remove_receipt_from_temp
from .statereader import get_public_key_from_wallet_address
from ..constants import NEWRL_DB


def store_receipt_to_db(receipt):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    wallet_cursor = cur.execute(
        'SELECT wallet_address FROM wallets where wallet_public=?', (receipt['public_key'],)).fetchone()
    
    if wallet_cursor is not None:
        
        db_receipt_data = (
            receipt['data']['block_index'],
            receipt['data']['block_hash'],
            receipt['data']['vote'],
            wallet_cursor[0],
        )

        cur.execute('''
            INSERT OR IGNORE INTO receipts (block_index, block_hash, vote, wallet_address)
            VALUES(?, ?, ?, ?)
        ''', db_receipt_data)
    
    con.commit()
    con.close()


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
        wallet_cursor = cur.execute(
        'SELECT wallet_address FROM wallets where wallet_public=?', 
        (receipt['public_key'],)).fetchone()
        if wallet_cursor is not None:
            wallet_address = wallet_cursor[0]
            db_receipt_data = (
                receipt['data']['block_index'],
                receipt['data']['block_hash'],
                receipt['data']['vote'],
                wallet_address,
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
                wallet_address)