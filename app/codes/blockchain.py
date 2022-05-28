"""Python programm to create object that enables addition of a block"""
import time
import datetime
import hashlib
import json

import sqlite3

from app.codes.clock.global_time import get_corrected_time_ms
from app.codes.receiptmanager import update_receipts_in_state

from .fs.temp_manager import remove_block_from_temp
from ..constants import BLOCK_TIME_INTERVAL_SECONDS, NEWRL_DB, NO_BLOCK_TIMEOUT
from .utils import get_time_ms
from .crypto import calculate_hash
from .state_updater import update_db_states, update_trust_scores
from .utils import get_time_ms
from .auth.auth import get_node_wallet_address
from .fs.mempool_manager import remove_transaction_from_mempool


class Blockchain:
    """Main blockchain related functions"""

    def __init__(self) -> None:
        self.chain = []

    def create_block(self, cur, block, block_hash, creator_wallet=None):
        """Create a block and store to db"""
        transactions_hash = self.calculate_hash(block['text']['transactions'])
        db_block_data = (
            block['index'],
            block['timestamp'],
            block['proof'],
            block['previous_hash'],
            block_hash,
            creator_wallet,
            transactions_hash
        )
        cur.execute('INSERT OR IGNORE INTO blocks (block_index, timestamp, proof, previous_hash, hash, creator_wallet, transactions_hash) VALUES (?, ?, ?, ?, ?, ?, ?)', db_block_data)
        return block

    def get_block(self, block_index):
        con = sqlite3.connect(NEWRL_DB)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        block_cursor = cur.execute(
            'SELECT * FROM blocks where block_index=?', (block_index,)).fetchone()
        
        if block_cursor is None:
            return None
        block = dict(block_cursor)

        transactions_cursor = cur.execute(
            'SELECT * FROM transactions where block_index=?', (block_index,)).fetchall()
        transactions = [dict(ix) for ix in transactions_cursor]
        transactions = list(map(lambda t: 
            {'transaction': t, 'signatures': [] if t['signatures'] is None else json.loads(t['signatures'])},
            transactions))
        block['text'] = {
            'transactions': transactions,
        }

        return block

    def proof_of_work(self, block):
        """Proof of work which takes a block with proof set as 0 as input and 
           returns the proof that makes its hash start with 0000"""
        proof = 1
        block_hash = ''

        while block_hash[:4] != '0000':
            block['proof'] = proof
            block_hash = self.calculate_hash(block)
            proof += 1

        return block_hash

    def calculate_hash(self, block):
        """Calculate hash of a given block using sha256"""
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        """Validate a chain using previous hash and starting bytes"""
        if len(chain) == 0:
            return True

        previous_block_hash = self.calculate_hash(chain[0])
        for block in chain[1:]:
            if block['previous_hash'] != previous_block_hash:
                return False

            if previous_block_hash[:4] != '0000':
                return False
            previous_block_hash = self.calculate_hash(block)

        return True

    def mine_block(self, cur, text, fees=0):
        """Mine a new block"""
        print("Starting the mining step 1")
        last_block_cursor = cur.execute(
            'SELECT block_index, hash FROM blocks ORDER BY block_index DESC LIMIT 1')
        last_block = last_block_cursor.fetchone()
        last_block_index = last_block[0] if last_block is not None else 0
        last_block_hash = last_block[1] if last_block is not None else 0

        block = {
            'index': last_block_index + 1,
            'timestamp': get_corrected_time_ms(),
            'proof': 0,
            'text': text,
            'creator_wallet': get_node_wallet_address(),
            'previous_hash': last_block_hash
        }

        block_hash = self.proof_of_work(block)
        print("New block hash is ", block_hash)

        block = self.create_block(cur, block, block_hash)
        return block

    def propose_block(self, cur, text):
        """Propose a new block and not add to chain"""
        last_block_cursor = cur.execute(
            'SELECT block_index, hash FROM blocks ORDER BY block_index DESC LIMIT 1')
        last_block = last_block_cursor.fetchone()
        last_block_index = last_block[0] if last_block is not None else 0
        last_block_hash = last_block[1] if last_block is not None else 0
        print(f'Proposing a block with index {last_block_index + 1}')

        block = {
            'index': last_block_index + 1,
            'timestamp': get_corrected_time_ms(),
            'proof': 0,
            'text': text,
            'creator_wallet': get_node_wallet_address(),
            'previous_hash': last_block_hash
        }
        return block

    def mine_empty_block(self, new_block_timestamp=None):
        """Mine an empty block"""
        print("Mining empty block")
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        last_block_cursor = cur.execute(
            'SELECT block_index, hash, timestamp FROM blocks ORDER BY block_index DESC LIMIT 1')
        last_block = last_block_cursor.fetchone()
        con.close()
        last_block_index = last_block[0] if last_block is not None else 0
        last_block_hash = last_block[1] if last_block is not None else 0
        last_block_timestamp = last_block[2] if last_block is not None else 0

        EMPTY_BLOCK_NONCE = 42

        if new_block_timestamp is None:
            new_block_timestamp = int(last_block_timestamp) + (BLOCK_TIME_INTERVAL_SECONDS + NO_BLOCK_TIMEOUT) * 1000

        block = {
            'index': last_block_index + 1,
            'timestamp': new_block_timestamp,
            'proof': EMPTY_BLOCK_NONCE,
            'text': {"transactions": [], "signatures": []},
            'creator_wallet': None,
            'previous_hash': last_block_hash
        }

        return block

    def get_latest_ts(self, cur=None):
        """Get the timestamp of latest block"""
        should_close_db_conn = False
        if not cur:
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            should_close_db_conn = True
        last_block_cursor = cur.execute(
            'SELECT block_index, timestamp FROM blocks ORDER BY block_index DESC LIMIT 1')
        last_block = last_block_cursor.fetchone()
        if last_block is None:
            ts = None
        else:
            ts = last_block[1]
        if should_close_db_conn:
            con.close()
        return ts


def add_block(cur, block, block_hash):
    """Add a block to db, add transactions and update states"""
    last_block = get_last_block(cur)
    if last_block is not None and last_block['hash'] != block['previous_hash']:
        print('Previous block hash does not match current block data')
        return
    # Needed for backward compatibility of blocks
    block_index = block['block_index'] if 'block_index' in block else block['index']
    # transactions_hash = block['transactions_hash'] if 'transactions_hash' in block else ''
    transactions_hash = calculate_hash(block['text']['transactions'])
    print('Adding block', block_index)
    db_block_data = (
        block_index,
        block['timestamp'],
        block['proof'],
        block['previous_hash'],
        block_hash,
        block['creator_wallet'],
        transactions_hash
    )
    cur.execute('INSERT OR IGNORE INTO blocks (block_index, timestamp, proof, previous_hash, hash, creator_wallet, transactions_hash) VALUES (?, ?, ?, ?, ?, ?, ?)', db_block_data)
    update_db_states(cur, block)
    # update_receipts_in_state(cur, block)
    # update_trust_scores(cur, block)

    for transaction in block['text']['transactions']:
        transaction = transaction['transaction']
        transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction['trans_code']
        remove_transaction_from_mempool(transaction_code)
    remove_block_from_temp(block_index)


def get_last_block_index():
    """Get last block index from db"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    last_block_cursor = cur.execute(
        'SELECT block_index FROM blocks ORDER BY block_index DESC LIMIT 1'
    )
    last_block = last_block_cursor.fetchone()
    con.close()
    return last_block[0] if last_block is not None else 0


def get_last_block(cur=None):
    """Get last block hash from db"""
    cursor_opened_inside = False
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened_inside = True
    last_block_cursor = cur.execute(
        'SELECT block_index, hash, timestamp FROM blocks ORDER BY block_index DESC LIMIT 1'
    )
    last_block = last_block_cursor.fetchone()

    if cursor_opened_inside:
        con.close()

    if last_block is not None:
        return {
            'index': last_block[0],
            'hash': last_block[1],
            'timestamp': last_block[2]
        }
    else:
        return None


def block_exists(block_index):
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        block_cursor = cur.execute(
            'SELECT * FROM blocks where block_index=?', (block_index,)).fetchone()
        
        if block_cursor is not None:
            block_exists = True
        else:
            block_exists = False
        
        con.close()
        return block_exists
