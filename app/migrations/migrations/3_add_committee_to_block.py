import sqlite3

from app.constants import NEWRL_DB
from app.nvalues import DAO_MANAGER, ASQI_WALLET


def migrate():
    print("Adding committee column to block")
    
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    try:
        cur.execute(f'''
            ALTER TABLE blocks ADD COLUMN expected_miner TEXT;
        ''')    
        cur.execute(f'''
            ALTER TABLE blocks ADD COLUMN committee TEXT;
        ''')
    except Exception as e:
        print('Column expected_miner already exists')
    try:
        cur.execute(f'''
            ALTER TABLE blocks ADD COLUMN committee TEXT;
        ''')
    except Exception as e:
        print('Column committee already exists')

    con.commit()
    con.close()