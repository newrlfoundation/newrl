import sqlite3

from app.constants import NEWRL_DB
from app.nvalues import DAO_MANAGER, ASQI_WALLET, STAKE_CT_ADDRESS


def migrate():
    print("Migrating STAKE CONTRACT")
    init_stake_contract()


def init_stake_contract():
    """Initialise Stake contract."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_stake_contract(cur, STAKE_CT_ADDRESS)

    con.commit()
    con.close()


def create_stake_contract(cur, address):
    query_params = (
        address,
        ASQI_WALLET,
        1648706655,
        'NewrlStakeContract',
        '1.0.0',
        'hybrid',
        '1',
        None,
        '{"setup": null, "deploy": null, "create": null, "stake_tokens": null, "unstake_tokens": null}',
        None,
        '{}',
        '1',
        '{}',
        '{}'
    )
    contract_exists = cur.execute(f'''SELECT COUNT(*) FROM CONTRACTS WHERE ADDRESS=? AND NAME LIKE ? ''',
                                     (address, 'NewrlStakeContract'))
    contract_exists = contract_exists.fetchone()
    if (contract_exists[0] == 0):
        cur.execute(f'''INSERT OR IGNORE INTO CONTRACTS
            (address, creator, ts_init, 
            name, version, actmode, status,next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)



if __name__ == '__main__':
    # migrate()
    pass
