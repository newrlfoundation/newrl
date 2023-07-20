import sqlite3
import json
import os
import logging

from app.core.db.dbmanager import revert_to_last_snapshot
from app.core.fs.archivemanager import get_block_from_archive

from ..core.blockchain.blockchain import Blockchain, add_block
from ..core.blockchain import blockchain
from app.core.blockchain.state_updater import add_block_reward, update_state_from_transaction, update_trust_scores
from ..core.consensus.receiptmanager import update_receipts_in_state
from .migrate_db import run_migrations
from app.config.constants import NEWRL_DB, NEWRL_P2P_DB
from ..core.clock.timers import SYNC_STATUS
from app.config.constants import BLOCK_ARCHIVE_PATH

db_path = NEWRL_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_db():
    os.remove(NEWRL_DB)
    # con = sqlite3.connect(db_path)
    # cur = con.cursor()
    # cur.execute('DROP TABLE IF EXISTS wallets')
    # cur.execute('DROP TABLE IF EXISTS tokens')
    # cur.execute('DROP TABLE IF EXISTS balances')
    # cur.execute('DROP TABLE IF EXISTS blocks')
    # cur.execute('DROP TABLE IF EXISTS receipts')
    # cur.execute('DROP TABLE IF EXISTS transactions')
    # cur.execute('DROP TABLE IF EXISTS transfers')
    # cur.execute('DROP TABLE IF EXISTS contracts')
    # cur.execute('DROP TABLE IF EXISTS miners')
    # cur.execute('DROP TABLE IF EXISTS kyc')
    # cur.execute('DROP TABLE IF EXISTS person')
    # cur.execute('DROP TABLE IF EXISTS person_wallet')
    # cur.execute('DROP TABLE IF EXISTS trust_scores')
    # cur.execute('DROP TABLE IF EXISTS dao_main')
    # cur.execute('DROP TABLE IF EXISTS dao_membership')
    # cur.execute('DROP TABLE IF EXISTS proposal_data')
    # cur.execute('DROP TABLE IF EXISTS DAO_TOKEN_LOCK')
    # cur.execute('DROP TABLE IF EXISTS stake_ledger')
    # cur.execute('DROP TABLE IF EXISTS configuration')
    # con.commit()
    # con.close()

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
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_wallet_public ON wallets (wallet_public)
                ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS tokens
                    (tokencode text NOT NULL PRIMARY KEY, 
                    tokenname text,
                    tokentype integer,
                    first_owner text,
                    custodian text,
                    legaldochash text,
                    amount_created integer,
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
                    balance integer, UNIQUE (wallet_address, tokencode))
                    ''')
    # cur.execute('''
    #                 CREATE UNIQUE INDEX IF NOT EXISTS idx_balances_wallet_address ON balances (wallet_address)
    #             ''')
    # cur.execute('''
    #                 CREATE UNIQUE INDEX IF NOT EXISTS idx_balances_tokencode ON balances (tokencode)
    #             ''')
    cur.execute('DROP INDEX IF EXISTS idx_balances_wallet_address')
    cur.execute('DROP INDEX IF EXISTS idx_balances_tokencode')
    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_balances_wallet_address_tokencode
                     ON balances (wallet_address, tokencode)
                ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS blocks
                    (block_index integer PRIMARY KEY,
                    timestamp integer,
                    proof integer,
                    status integer,
                    previous_hash text,
                    hash text,
                    creator_wallet text,
                    expected_miner text,
                    committee text)
                    ''')
    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_block_hash ON blocks (hash)
                ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS receipts
                    (block_index integer,
                    block_hash text,
                    vote integer,
                    wallet_address text)
                    ''')

    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_receipts_block_index_hash
                     ON receipts (block_index, block_hash, wallet_address)
                ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS transactions
                    (
                    transaction_code text PRIMARY KEY,
                    block_index integer,
                    status integer,
                    exec_msg text
                 )
                    ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS transfers
                    (transaction_code text,
                    asset1_code integer,
                    asset2_code integer,
                    wallet1 text,
                    wallet2 text,
                    asset1_number integer
                    asset2_number integer)
                    ''')
    
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS contracts
                    (address TEXT NOT NULL PRIMARY KEY,
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
                    last_broadcast_timestamp integer,
                    block_index integer,
                    UNIQUE (wallet_address)
                    )
                    ''')
    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS miners_wallet_address_timestamp
                     ON miners (wallet_address, last_broadcast_timestamp)
                ''')

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
                    (person_id text NOT NULL, 
                    wallet_id text NOT NULL PRIMARY KEY)
                    ''')
    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_person_wallet_wallet_id
                    ON person_wallet (wallet_id)
                ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS trust_scores
                    (src_person_id text NOT NULL, 
                    dest_person_id text NOT NULL,
                    score integer,
                    last_time integer,
                    UNIQUE (src_person_id, dest_person_id)
                    )
                    ''')
    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_trust_scores ON trust_scores (src_person_id, dest_person_id)
                ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS dao_main
                    (
                    address text NOT NULL,
                    dao_personid text NOT NULL, 
                    dao_name text NOT NULL,
                    founder_personid text NOT NULL,
                    dao_sc_address text  PRIMARY KEY NOT NULL)
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS dao_membership
                    (address text NOT NULL,
                    dao_person_id text NOT NULL, 
                    member_person_id text NOT NULL,
                    role INT )
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS proposal_data
                    (
                    address text NOT NULL,
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
                    CREATE TABLE IF NOT EXISTS dao_token_lock
                    (
                    address text NOT NULL,
                    dao_id  text Not NULL,
                    person_id text Not NULL,
                    proposal_list TEXT ,
                    status INT,
                    amount_locked INT,
                    wallet_address text
                    )
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS stake_ledger 
                    (
                    address text NOT NULL, 
                    person_id text Not NULL, 
                    wallet_address TEXT , 
                    amount INT, 
                    time_updated TIMESTAMP,
                    staker_wallet_address text
                    )
                    ''')
    cur.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_stake_ledger_address_person_id
                    ON stake_ledger (address,person_id)
                ''')
    cur.execute('''
                        CREATE TABLE IF NOT EXISTS configuration 
                        (
                        address text NOT NULL,
                        property_key text PRIMARY KEY NOT NULL, 
                        property_value text Not NULL, 
                        is_editable TEXT , 
                        last_updated TIMESTAMP 
                        )
                        ''')

    cur.execute('''
                    CREATE TABLE IF NOT EXISTS sample_template
                    (
                    address text NOT NULL,
                    wallet_address text NOT NULL,
                    name text    
                    )
    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS pledge_ledger 
                    (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address text NOT NULL, 
                    borrower text Not NULL, 
                    lender text Not NULL , 
                    amount INT, 
                    token_code text not NULL,
                    time_updated TIMESTAMP,
                    status INT,
                    unique_column text not NULL ,
                    pledge_status text
                    )
                    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS alias
                    (
                    identifier text  NOT NULL,
                    wallet_address text NOT NULL,
                    address text NOT NULL,
                    PRIMARY KEY (identifier, wallet_address)
                    )
    ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS verification 
                    (
                    address text NOT NULL,
                    asset_id text NOT NULL,
                    asset_type text NOT NULL, 
                    verifier_address text NOT NULL,
                    outcome INT Not NULL, 
                    doc_hash_list text, 
                    doc_link_list text, 
                    remarks text,
                    deletable_after INT
                    )
                    ''')
    con.commit()
    con.close()


def revert_chain_quick(revert_to_snapshot=True):
    SYNC_STATUS['IS_SYNCING'] = True
    if revert_to_snapshot:
        revert_to_last_snapshot()
    else:
        clear_db()
        init_db()
        run_migrations()
    SYNC_STATUS['IS_SYNCING'] = False


def revert_chain(block_index):
    """Revert chain to given index"""
    logger.info(f'Reverting chain to local snapshot.')
    global SYNC_STATUS
    if SYNC_STATUS['IS_SYNCING']:
        logger.info('Syncing with network. Reverting anyway.')
        # logger.info('Syncing with network. Aborting revert.')
        # return
    # revert_to_last_snapshot()
    # return
    SYNC_STATUS['IS_SYNCING'] = True
    try:
        if block_index == 0:
            clear_db()
        else:
            revert_to_last_snapshot()
            SYNC_STATUS['IS_SYNCING'] = False
            return
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            cur.execute(f'DELETE FROM blocks WHERE block_index > {block_index}')
            cur.execute(f'DELETE FROM transactions WHERE block_index > {block_index}')
            cur.execute(f'DELETE FROM receipts WHERE included_block_index > {block_index}')
            cur.execute('DROP TABLE IF EXISTS wallets')
            cur.execute('DROP TABLE IF EXISTS tokens')
            cur.execute('DROP TABLE IF EXISTS balances')
            # cur.execute('DROP TABLE IF EXISTS blocks')
            # cur.execute('DROP TABLE IF EXISTS receipts')  # TODO - Remove this
            # cur.execute('DROP TABLE IF EXISTS transactions')
            cur.execute('DROP TABLE IF EXISTS transfers')
            cur.execute('DROP TABLE IF EXISTS contracts')
            cur.execute('DROP TABLE IF EXISTS miners')
            cur.execute('DROP TABLE IF EXISTS kyc')
            cur.execute('DROP TABLE IF EXISTS person')
            cur.execute('DROP TABLE IF EXISTS person_wallet')
            cur.execute('DROP TABLE IF EXISTS trust_scores')
            cur.execute('DROP TABLE IF EXISTS dao_main')
            cur.execute('DROP TABLE IF EXISTS dao_membership')
            cur.execute('DROP TABLE IF EXISTS proposal_data')
            cur.execute('DROP TABLE IF EXISTS DAO_TOKEN_LOCK')
            cur.execute('DROP TABLE IF EXISTS stake_ledger')
            cur.execute('DROP TABLE IF EXISTS configuration')
            # TODO - Drop all trust tables too
            con.commit()
            con.close()

        init_db()
        run_migrations()

        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()

        chain = Blockchain()
        for _block_index in range(1, block_index):
            block = chain.get_block(_block_index)
            add_block(cur, block, is_state_reconstruction=True)

        con.commit()
        con.close()
    except Exception as e:
        logger.error(f'Error reverting {str(e)}')
    SYNC_STATUS['IS_SYNCING'] = False
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

def clear_state_and_make_from_archive():
    revert_chain_quick(revert_to_snapshot=False)

    block_index = 1

    while True:
        logger.info(f'Adding block: {block_index}')
        block = get_block_from_archive(block_index)
        if block is None:
            logger.info(f'Finished archive block at index: {block_index}')
            break
        con = sqlite3.connect(NEWRL_DB, timeout=10)
        cur = con.cursor()
        blockchain.add_block(cur, block)
        con.commit()
        con.close()
        block_index += 1


if __name__ == '__main__':
    db_path = '../' + db_path
    # clear_db()
    init_db()