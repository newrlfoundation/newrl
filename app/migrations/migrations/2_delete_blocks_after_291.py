import sqlite3
import json

from ..init_db import init_db

from ...codes.state_updater import update_state_from_transaction

from ...constants import NEWRL_DB


def migrate():
    pass
    # print('Running migration ' + __file__)
    # revert_chain(291)

def revert_chain(block_index):
    """Revert chain to given index"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    cur.execute(f'DELETE FROM blocks WHERE block_index > {block_index}')
    cur.execute(f'DELETE FROM transactions WHERE block_index > {block_index}')
    cur.execute('DROP TABLE wallets')
    cur.execute('DROP TABLE tokens')
    cur.execute('DROP TABLE balances')
    con.commit()

    init_db()

    transactions_cursor = cur.execute(f'SELECT transaction_code, block_index, type, timestamp, specific_data FROM transactions WHERE block_index <= {block_index}').fetchall()
    for transaction in transactions_cursor:
        transaction_code = transaction[0]
        block_index = transaction[1]
        transaction_type = transaction[2]
        timestamp = transaction[3]
        specific_data = transaction[4]
        while isinstance(specific_data, str):
            specific_data = json.loads(specific_data)

        update_state_from_transaction(cur, transaction_type, specific_data, transaction_code, timestamp)

    con.commit()
    con.close()


if __name__ == '__main__':
    # migrate()
    pass
