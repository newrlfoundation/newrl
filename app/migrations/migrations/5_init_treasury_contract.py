import json
import sqlite3

from app.constants import NEWRL_DB
from app.nvalues import DAO_MANAGER, ASQI_WALLET, TREASURY_CONTRACT_ADDRESS, FOUNDATION_WALLET


def migrate():
    print("Migrating TREASURY CONTRACT")
    init_treasury_contract()


def init_treasury_contract():
    """Initialise Dao_Manager."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_treasury_contract(cur, TREASURY_CONTRACT_ADDRESS)

    con.commit()
    con.close()


def create_treasury_contract(cur, address):
    address_signatories = [ASQI_WALLET, FOUNDATION_WALLET]
    signatories = {"setup": None,
                   "deploy": None,
                   "burn_token": address_signatories,
                   "upgrade_transfer": address_signatories,
                   "payout": address_signatories
                   }
    query_params = (
        address,
        ASQI_WALLET,
        1648706655,
        'TreasuryContract',
        '1.0.0',
        'hybrid',
        '1',
        None,
        json.dumps(signatories),
        None,
        '{}',
        '1',
        '{}',
        '{}'
    )
    treasury_contract_exist = cur.execute(f'''SELECT COUNT(*) FROM CONTRACTS WHERE ADDRESS=? AND NAME LIKE ? ''',
                                          (address, 'TreasuryContract'))
    treasury_contract_exist = treasury_contract_exist.fetchone()
    if treasury_contract_exist[0] == 0:
        cur.execute(f'''INSERT OR IGNORE INTO CONTRACTS
            (address, creator, ts_init, 
            name, version, actmode, status,next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)


if __name__ == '__main__':
    # migrate()
    pass
