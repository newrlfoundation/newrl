"""Receipt manager"""

import sqlite3

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


def get_receipts_for_block_from_db(block_index):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    receipt_cursor = cur.execute(
        'SELECT * FROM receipts where block_index=?', (block_index,))
    
    # if receipt_cursor is None:
    #     return []
    receipts = receipt_cursor.fetchall()

    return receipts


def update_receipts_in_state(cur, block):
    receipts = block['text']['previous_block_receipts']

    for receipt in receipts:
        wallet_cursor = cur.execute(
        'SELECT wallet_address FROM wallets where wallet_public=?', 
        (receipt['public_key'],)).fetchone()
    
        if wallet_cursor is not None:
            db_receipt_data = (
                receipt['data']['block_index'],
                receipt['data']['block_hash'],
                receipt['data']['vote'],
                receipt['timestamp'],
                wallet_cursor[0],
            )

            cur.execute('''
                INSERT OR IGNORE INTO receipts 
                (block_index, block_hash, vote, timestamp, wallet_address)
                VALUES(?, ?, ?, ?, ?)
            ''', db_receipt_data)
