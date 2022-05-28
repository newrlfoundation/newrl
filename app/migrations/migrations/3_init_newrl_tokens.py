import sqlite3

from ...ntypes import NEWRL_TOKEN_CODE, NEWRL_TOKEN_NAME

from ...constants import NEWRL_DB

FOUNDATION_WALLET = '0xc29193dbab0fe018d878e258c93064f01210ec1a'
ASQI_WALLET = '0x20513a419d5b11cd510ae518dc04ac1690afbed6'
FOUNDATION_PUBLIC_KEY = 'sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg=='
ASQI_PUBLIC_KEY = 'PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg=='

FOUNDATION_RESERVE = 3000000000

def migrate():
    init_newrl_tokens()

def init_newrl_tokens():
    """Initialise NWRL tokens and pay the foundation"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_newrl_tokens(cur, FOUNDATION_RESERVE * 2)
    create_wallet(cur, FOUNDATION_WALLET, FOUNDATION_PUBLIC_KEY)
    create_wallet(cur, ASQI_WALLET, ASQI_PUBLIC_KEY)
    credit_wallet(cur, FOUNDATION_WALLET, FOUNDATION_RESERVE)
    credit_wallet(cur, ASQI_WALLET, FOUNDATION_RESERVE)

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
    

if __name__ == '__main__':
    # migrate()
    pass
