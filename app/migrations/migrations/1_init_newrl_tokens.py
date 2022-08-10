import sqlite3

from app.Configuration import Configuration
from ...ntypes import NEWRL_TOKEN_CODE, NEWRL_TOKEN_NAME

from ...constants import NEWRL_DB


FOUNDATION_RESERVE = 3000000000

def migrate():
    init_newrl_tokens()

def init_newrl_tokens():
    """Initialise NWRL tokens and pay the foundation"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_wallet(cur, Configuration.config("FOUNDATION_WALLET"), Configuration.config("FOUNDATION_WALLET_PUBLIC"))
    create_wallet(cur, Configuration.config("ASQI_WALLET"), Configuration.config("ASQI_WALLET_PUBLIC"))
    create_wallet(cur, Configuration.config("SENTINEL_NODE_WALLET"), Configuration.config("SENTINEL_NODE_WALLET_PUBLIC"))
    create_wallet(cur, Configuration.config("NETWORK_TRUST_MANAGER_WALLET"), Configuration.config("NETWORK_TRUST_MANAGER_PUBLIC"))

    create_newrl_tokens(cur, FOUNDATION_RESERVE * 2)
    
    credit_wallet(cur, Configuration.config("FOUNDATION_WALLET"), FOUNDATION_RESERVE)
    credit_wallet(cur, Configuration.config("ASQI_WALLET"), FOUNDATION_RESERVE)

    create_person(cur, Configuration.config("ASQI_PID"))
    link_person_wallet(cur, Configuration.config("ASQI_PID"), Configuration.config("ASQI_WALLET"))
    create_person(cur, Configuration.config("NETWORK_TRUST_MANAGER_PID"))
    link_person_wallet(cur, Configuration.config("NETWORK_TRUST_MANAGER_PID"), Configuration.config("NETWORK_TRUST_MANAGER_WALLET"))

    con.commit()
    con.close()


def create_newrl_tokens(cur, amount):
    query_params = (
            NEWRL_TOKEN_CODE,
            NEWRL_TOKEN_NAME,
            '1',
            amount,
            False,
            0,
            '{}',
        )
    cur.execute(f'''INSERT OR IGNORE INTO tokens
        (tokencode, tokenname, tokentype, 
        amount_created, sc_flag, tokendecimal, token_attributes)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)

def create_wallet(cur, wallet_address, wallet_public):
    query_params = (wallet_address,
                    wallet_public,
                    '', '{}', '1', '91', '{}'
                    )
    cur.execute(f'''INSERT OR IGNORE INTO wallets
            (wallet_address, wallet_public, custodian_wallet, kyc_docs, 
            owner_type, jurisdiction, specific_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)    

def credit_wallet(cur, wallet, amount):
    cur.execute(f'''INSERT OR IGNORE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet, NEWRL_TOKEN_CODE, amount))

def create_person(cur, person_id):
    query_params = (person_id, 0)
    cur.execute(f'''INSERT OR IGNORE INTO person
                (person_id, created_time)
                VALUES (?, ?)''', query_params)

def link_person_wallet(cur, person_id, wallet_address):
    query_params = (person_id, wallet_address)
    cur.execute(f'''INSERT OR IGNORE INTO person_wallet
                (person_id, wallet_id)
                VALUES (?, ?)''', query_params)


if __name__ == '__main__':
    # migrate()
    pass
