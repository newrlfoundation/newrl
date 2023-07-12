import json
import sqlite3

from app.core.helpers.utils import get_person_id_for_wallet_address
from app.config.constants import NEWRL_DB
from app.config.nvalues import CUSTODIAN_DAO_ADDRESS, CUSTODIAN_WALLET_LIST, DAO_MANAGER, ASQI_WALLET, FOUNDATION_WALLET, ASQI_DAO_ADDRESS, \
    ASQI_WALLET_DAO, FOUNDATION_WALLET_DAO, FOUNDATION_DAO_ADDRESS, MEMBER_WALLET_LIST


def migrate():
    print("Updating transaction status")
    add_transaction_status_main()


def add_transaction_status_main():
    """Update Custodian DAO."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    add_transaction_status(cur)
    add_transaction_exec_msg(cur)
    con.commit()
    con.close()


def add_transaction_status(cur):
    
    try:
        cur.execute(f'''ALTER TABLE transactions ADD status INTEGER ''')
    except Exception as e:
        print('Error adding status to transaction table', str(e))   

    pass

def add_transaction_exec_msg(cur):
    
    try:
        cur.execute(f'''ALTER TABLE transactions ADD exec_msg TEXT ''')
    except Exception as e:
        print('Error adding exec_msg to transaction table', str(e))   

    pass
