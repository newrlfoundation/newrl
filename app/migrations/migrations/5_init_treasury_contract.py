import json
import math
import sqlite3

from app.constants import NEWRL_DB
from app.ntypes import NEWRL_TOKEN_DECIMAL
from app.nvalues import DAO_MANAGER, ASQI_WALLET, TREASURY_CONTRACT_ADDRESS, FOUNDATION_WALLET, ASQI_TREASURY_ADDRESS, \
    FOUNDATION_TREASURY_ADDRESS, NETWORK_TREASURY_ADDRESS, FOUNDATION_DAO_ADDRESS, ASQI_DAO_ADDRESS


def migrate():
    print("Migrating TREASURY CONTRACT")
    init_treasury_contract()


def create_network_contract(cur, address,dao_address=FOUNDATION_DAO_ADDRESS):
    address_signatories = None
    signatories = {"setup": None,
                   "deploy": None,
                   "burn_token": address_signatories,
                   "upgrade_transfer": address_signatories,
                   "payout": address_signatories
                   }
    contract_specs = {"dao_address": dao_address,
                      "recipient_list": []
                      }
    query_params = (
        address,
        ASQI_WALLET,
        1648706655,
        'NetworkContract',
        '1.0.0',
        'hybrid',
        '1',
        None,
        json.dumps(signatories),
        None,
        '{}',
        '1',
        json.dumps(contract_specs),
        '{}'
    )
    treasury_contract_exist = cur.execute(f'''SELECT COUNT(*) FROM CONTRACTS WHERE ADDRESS=? AND NAME LIKE ? ''',
                                          (address, 'NetworkContract'))
    treasury_contract_exist = treasury_contract_exist.fetchone()
    if treasury_contract_exist[0] == 0:
        cur.execute(f'''INSERT OR IGNORE INTO CONTRACTS
                (address, creator, ts_init, 
                name, version, actmode, status,next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)


    pass


def init_treasury_contract():
    """Initialise Dao_Manager."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_network_contract(cur, NETWORK_TREASURY_ADDRESS)
    create_treasury_contract(cur, ASQI_TREASURY_ADDRESS,ASQI_DAO_ADDRESS)
    create_treasury_contract(cur, FOUNDATION_TREASURY_ADDRESS,FOUNDATION_DAO_ADDRESS)

    con.commit()
    con.close()


def create_treasury_contract(cur, address,dao_address=FOUNDATION_DAO_ADDRESS):
    address_signatories = None
    signatories = {"setup": None,
                   "deploy": None,
                   "burn_token": address_signatories,
                   "upgrade_transfer": address_signatories,
                   "payout": address_signatories
                   }
    multiplier_newrl=math.pow(10,NEWRL_TOKEN_DECIMAL)
    transfer_limits = [
        0,
        0,
        1000000*multiplier_newrl,
        10000000*multiplier_newrl,
        50000000*multiplier_newrl,
        100000000*multiplier_newrl,
        100000000*multiplier_newrl,
        100000000*multiplier_newrl
    ]

    contract_specs = {
        "dao_address":dao_address,
        "transfer_limits":json.dumps(transfer_limits)
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
        json.dumps(contract_specs),
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
