import sqlite3

from ...constants import NEWRL_DB


def migrate():
    optimize_db()

def optimize_db():
    """Remove redundant columns for db size reduction"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    try:
        cur.execute('ALTER TABLE receipts DROP COLUMN included_block_index')    
        cur.execute('ALTER TABLE receipts DROP COLUMN signature')    
        cur.execute('ALTER TABLE receipts DROP COLUMN timestamp')    
        cur.execute('DROP INDEX IF EXISTS idx_receipts_block_index_hash')
        cur.execute('ALTER TABLE transactions DROP COLUMN timestamp')    
        cur.execute('ALTER TABLE transactions DROP COLUMN type')    
        cur.execute('ALTER TABLE transactions DROP COLUMN currency')    
        cur.execute('ALTER TABLE transactions DROP COLUMN fee')    
        cur.execute('ALTER TABLE transactions DROP COLUMN description')    
        cur.execute('ALTER TABLE transactions DROP COLUMN valid')    
        cur.execute('ALTER TABLE transactions DROP COLUMN specific_data')    
        cur.execute('ALTER TABLE transactions DROP COLUMN signatures')    
        cur.execute('VACUUM')
    except:
        pass

    con.commit()
    con.close()
