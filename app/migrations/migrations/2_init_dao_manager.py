import sqlite3

from app.constants import NEWRL_DB

DAO_MANAGER = 'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7'
ASQI_WALLET = '0x20513a419d5b11cd510ae518dc04ac1690afbed6'


def migrate():
    print("Migrating DAO MANAGER")
    init_dao_manager()


def init_dao_manager():
    """Initialise Dao_Manager."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_dao_manager(cur, DAO_MANAGER)

    con.commit()
    con.close()


def create_dao_manager(cur, address):
    query_params = (
        address,
        ASQI_WALLET,
        1648706655,
        'dao_manager',
        '1.0.0',
        'hybrid',
        '1',
        None,
        '{"setup": null, "deploy": null, "create": null}',
        None,
        '{}',
        '1',
        '{}',
        '{}'
    )
    dao_manager_exists = cur.execute(f'''SELECT COUNT(*) FROM CONTRACTS WHERE ADDRESS=? AND NAME LIKE ? ''',
                                     (address, 'dao_manager'))
    dao_manager_exists = dao_manager_exists.fetchone()
    if (dao_manager_exists[0] == 0):
        cur.execute(f'''INSERT OR IGNORE INTO CONTRACTS
            (address, creator, ts_init, 
            name, version, actmode, status,next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
        try:
            cur.execute(f'''alter table DAO_TOKEN_LOCK add COLUMN wallet_address text''')
        except:
            pass


if __name__ == '__main__':
    # migrate()
    pass
