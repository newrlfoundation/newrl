import sqlite3

from ...constants import NEWRL_DB


def migrate():
    add_block_index()

def add_block_index():
    """Add block index to miners table"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    try:
        cur.execute(f'''
            ALTER TABLE miners ADD COLUMN block_index INTEGER;
        ''')    
    except:
        pass

    con.commit()
    con.close()
