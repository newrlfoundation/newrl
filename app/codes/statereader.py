import sqlite3

from app.constants import NEWRL_DB


def get_public_key_from_wallet_address(wallet_address, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        connection_opened = True
    else:
        connection_opened = False
    wallet_cursor = cur.execute(
        'SELECT wallet_public FROM wallets where wallet_address=?', (wallet_address,)).fetchone()
    if wallet_cursor is None:
        return None
    wallet = dict(wallet_cursor)
    if connection_opened:
        con.close()
    return wallet['wallet_public']
