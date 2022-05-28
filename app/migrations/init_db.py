import sqlite3
import json

from ..codes.state_updater import update_state_from_transaction
from .migrate_db import run_migrations
from ..constants import NEWRL_DB, NEWRL_P2P_DB

db_path = NEWRL_DB

def clear_db():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS wallets')
    cur.execute('DROP TABLE IF EXISTS tokens')
    cur.execute('DROP TABLE IF EXISTS balances')
    cur.execute('DROP TABLE IF EXISTS blocks')
    cur.execute('DROP TABLE IF EXISTS transactions')
    cur.execute('DROP TABLE IF EXISTS transfers')
    cur.execute('DROP TABLE IF EXISTS receipts')
    cur.execute('DROP TABLE IF EXISTS contracts')
    cur.execute('DROP TABLE IF EXISTS miners')
    cur.execute('DROP TABLE IF EXISTS dao_main')
    cur.execute('DROP TABLE IF EXISTS dao_membership')
    con.commit()
    con.close()

def init_db():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS wallets
                    (wallet_address text NOT NULL PRIMARY KEY, 
                    wallet_public text,
                    wallet_private text,
                    custodian_wallet text,
                    kyc_docs text,
                    owner_type integer,
                    jurisdiction integer,
                    specific_data text)
                    ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS tokens
                    (tokencode text NOT NULL PRIMARY KEY, 
                    tokenname text,
                    tokentype integer,
                    first_owner text,
                    custodian text,
                    legaldochash text,
                    amount_created real,
                    sc_flag integer,
                    disallowed text,
                    tokendecimal integer,
                    parent_transaction_code text,
                    token_attributes text)
                    ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS balances
                    (wallet_address text, 
                    tokencode text,
                    balance real, UNIQUE (wallet_address, tokencode))
                    ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS blocks
                    (block_index integer PRIMARY KEY,
                    timestamp text,
                    proof integer,
                    previous_hash text,
                    hash text,
                    creator_wallet text,
                    transactions_hash text)
                    ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS receipts
                    (block_index integer,
                    block_hash text,
                    vote integer,
                    wallet_address text,
                    timestamp text)
                    ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS transactions
                    (
                    transaction_code text PRIMARY KEY,
                    block_index integer,
                    timestamp text,
                    type integer,
                    currency text,
                    fee real,
                    description text,
                    valid integer,
                    specific_data text,
                    signatures text)
                    ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS transfers
                    (transaction_code text,
                    asset1_code integer,
                    asset2_code integer,
                    wallet1 text,
                    wallet2 text,
                    asset1_number real
                    asset2_number real)
                    ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS contracts
                    (address TEXT,
                    creator TEXT,
                    ts_init INTEGER,
                    name TEXT,
                    version TEXT,
                    actmode TEXT,
                    status INTEGER,
                    next_act_ts INTEGER,
                    signatories TEXT,
                    parent TEXT,
                    oracleids TEXT,
                    selfdestruct INTEGER,
                    contractspecs TEXT,
                    legalparams TEXT)
                    ''')
    # cur.execute('DROP TABLE IF EXISTS miners')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS miners
                    (id text NOT NULL PRIMARY KEY,
                    wallet_address text,
                    network_address text NOT NULL,
                    last_broadcast_timestamp text,
                    UNIQUE (wallet_address)
                    )
                    ''')
    con.commit()
    con.close()


def init_trust_db():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS kyc
                    (id text NOT NULL PRIMARY KEY, 
                    doc_type text,
                    doc_number_hash text,
                    doc_hash text,
                    person_id text,
                    created_time text)
                    ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS person
                    (person_id text NOT NULL PRIMARY KEY, 
                    created_time integer)
                    ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS person_wallet
                    (person_id text NOT NULL PRIMARY KEY, 
                    wallet_id integer)
                    ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS trust_scores
                    (src_person_id text NOT NULL, 
                    dest_person_id text NOT NULL,
                    score real,
                    last_time integer)
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS dao_main
                    (dao_personid text NOT NULL, 
                    dao_name text NOT NULL,
                    founder_personid text NOT NULL,
                    dao_sc_address text NOT NULL)
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS dao_membership
                    (dao_person_id text NOT NULL, 
                    member_person_id text NOT NULL)
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS proposal_data
                    (
                    proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dao_person_id text NOT NULL, 
                    function_called text NOT NULL, 
                    params text , 
                    yes_votes INT , 
                    no_votes INT , 
                    abstain_votes INT , 
                    total_votes INT , 
                    status text NOT NULL, 
                    voting_start_ts text , 
                    voting_end_ts text ,
                    voter_data text
                    )
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS DAO_TOKEN_LOCK
                    (
                    dao_id  text Not NULL,
                    person_id text Not NULL,
                    pr  oposal_list TEXT ,
                    status INT,
                    amount_locked INT,
                    wallet_address text
                    )
                    ''')

    con.commit()
    con.close()


def revert_chain(block_index):
    """Revert chain to given index"""
    print('Reverting chain to index ', block_index)
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    cur.execute(f'DELETE FROM blocks WHERE block_index > {block_index}')
    cur.execute(f'DELETE FROM transactions WHERE block_index > {block_index}')
    cur.execute('DROP TABLE IF EXISTS wallets')
    cur.execute('DROP TABLE IF EXISTS tokens')
    cur.execute('DROP TABLE IF EXISTS balances')
    cur.execute('DROP TABLE IF EXISTS transfers')
    cur.execute('DROP TABLE IF EXISTS contracts')
    cur.execute('DROP TABLE IF EXISTS miners')
    con.commit()
    con.close()

    init_db()
    run_migrations()
    
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
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
    return {'status': 'SUCCESS'}


def init_peer_db():
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS peers
                    (id text NOT NULL PRIMARY KEY,
                    address text NOT NULL 
                    )
                    ''')
    # Todo - link node to a person and add record in the node db
    con.commit()
    con.close()


if __name__ == '__main__':
    db_path = '../' + db_path
    # clear_db()
    init_db()
