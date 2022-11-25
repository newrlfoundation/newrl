"""Chain and state queries"""
import sqlite3


from ..constants import NEWRL_DB
from .blockchain import Blockchain
from app.Configuration import Configuration

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



def download_state():
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    wallets_cursor = cur.execute('SELECT * FROM wallets ORDER BY wallet_address').fetchall()
    wallets = [dict(ix) for ix in wallets_cursor]

    tokens_cursor = cur.execute('SELECT * FROM tokens ORDER BY tokencode').fetchall()
    tokens = [dict(ix) for ix in tokens_cursor]

    balances_cursor = cur.execute('SELECT * FROM balances ORDER BY wallet_address').fetchall()
    balances = [dict(ix) for ix in balances_cursor]
    
    contracts_cursor = cur.execute('SELECT * FROM contracts ORDER BY address').fetchall()
    contracts = [dict(ix) for ix in contracts_cursor]
    
    miners_cursor = cur.execute('SELECT * FROM miners ORDER BY id').fetchall()
    miners = [dict(ix) for ix in miners_cursor]
    
    trust_scores_cursor = cur.execute('SELECT * FROM trust_scores ORDER BY src_person_id, dest_person_id').fetchall()
    trust_scores = [dict(ix) for ix in trust_scores_cursor]
    
    stake_ledger_cursor = cur.execute('SELECT * FROM stake_ledger ORDER BY address').fetchall()
    stake_ledger = [dict(ix) for ix in stake_ledger_cursor]
    
    con.close()
    state = {
        'wallets': wallets,
        'tokens': tokens,
        'balances': balances,
        'contracts': contracts,
        'miners': miners,
        'trust_scores': trust_scores,
        'stake_ledger': stake_ledger,
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
    con.close()
    if transaction_cursor is None:
        return None
    return dict(transaction_cursor)

def get_config():
    config = Configuration().conf
    return config

def get_wallet(wallet_address):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    wallet_cursor = cur.execute(
        'SELECT * FROM wallets where wallet_address=?', (wallet_address,)).fetchone()
    if wallet_cursor is None:
        return None
    wallet = dict(wallet_cursor)
    pid_cursor = cur.execute(
        'SELECT person_id FROM person_wallet WHERE wallet_id=?', (wallet['wallet_address'], ))
    pid = pid_cursor.fetchone()
    person_id = pid['person_id'] if pid is not None else ''
    wallet['person_id'] = person_id
    con.close()
    return wallet


def get_token(token_code):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur = cur.execute(
        'SELECT * FROM tokens where tokencode=?', (token_code,)).fetchone()
    con.close()
    if cur is None:
        return None
    return dict(cur)

def get_contract(contract_address):
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur = cur.execute(
        'SELECT * FROM contracts where address=?', (contract_address,)).fetchone()
    con.close()
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
