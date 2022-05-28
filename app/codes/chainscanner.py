"""Chain and state queries"""
import sqlite3

from ..constants import NEWRL_DB
from .blockchain import Blockchain


class Chainscanner():
    def __init__(self):
        self.blockchain = Blockchain()
        self.con = sqlite3.connect(NEWRL_DB)
        self.cur = self.con.cursor()

    def getbalancesbytoken(self, tokencode):
        """Get token balance across wallets"""
        balances = []
        balances_cur = self.cur.execute(
            'SELECT wallet_address, balance FROM balances WHERE tokencode = :tokencode', {'tokencode': tokencode})
        for row in balances_cur:
            print(row)
            balances.append({
                'wallet': row[0],
                'token_code': tokencode,
                'balance': row[1]
            })

        return balances

    def getbalancesbyaddress(self, address):
        """Get all tokens in address"""
        balances = []
        balances_cur = self.cur.execute(
            'SELECT tokencode, balance FROM balances WHERE wallet_address = :address', {'address': address})
        for row in balances_cur:
            print(row)
            balances.append({
                'wallet': address,
                'token_code': row[0],
                'balance': row[1]
            })

        return balances

    def getbaladdtoken(self, address, tokencode):
        balance = self.cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
                                   'address': address, 'tokencode': tokencode})
        for row in balance:
            return row[0]


def get_wallet_token_balance(wallet_address, token_code):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
        'address': wallet_address, 'tokencode': token_code})
    balance_row = balance_cursor.fetchone()
    balance = balance_row[0] if balance_row is not None else 0
    cur.close()
    return balance


def download_state():
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    wallets_cursor = cur.execute('SELECT * FROM wallets').fetchall()
    wallets = [dict(ix) for ix in wallets_cursor]

    tokens_cursor = cur.execute('SELECT * FROM tokens').fetchall()
    tokens = [dict(ix) for ix in tokens_cursor]

    balances_cursor = cur.execute('SELECT * FROM balances').fetchall()
    balances = [dict(ix) for ix in balances_cursor]
    
    contracts_cursor = cur.execute('SELECT * FROM contracts').fetchall()
    contracts = [dict(ix) for ix in contracts_cursor]

    state = {
        'wallets': wallets,
        'tokens': tokens,
        'balances': balances,
        'contracts': contracts
    }
    return state


def get_block(block_index):
    chain = Blockchain()
    return chain.get_block(block_index)

def get_transaction(transaction_code):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    transaction_cursor = cur.execute(
        'SELECT * FROM transactions where transaction_code=?', (transaction_code,)).fetchone()
    if transaction_cursor is None:
        return None
    return dict(transaction_cursor)


def get_wallet(wallet_address):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur = cur.execute(
        'SELECT * FROM wallets where wallet_address=?', (wallet_address,)).fetchone()
    if cur is None:
        return None
    return dict(cur)


def get_token(token_code):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur = cur.execute(
        'SELECT * FROM tokens where tokencode=?', (token_code,)).fetchone()
    if cur is None:
        return None
    return dict(cur)

def get_contract(contract_address):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur = cur.execute(
        'SELECT * FROM contracts where address=?', (contract_address,)).fetchone()
    if cur is None:
        return None
    return dict(cur)


def download_chain():
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    blocks_cursor = cur.execute('SELECT * FROM blocks').fetchall()
    blocks = [dict(ix) for ix in blocks_cursor]
    for idx, block in enumerate(blocks):
        print(block)
        transactions_cursor = cur.execute(
            'SELECT * FROM transactions where block_index=' + str(block['block_index'])).fetchall()
        transactions = [dict(ix) for ix in transactions_cursor]
        block[idx] = {
            'text': {
                'transactions': transactions
            }
        }
    print(blocks)

    chain = blocks
    return chain
