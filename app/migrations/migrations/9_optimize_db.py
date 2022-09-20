import sqlite3

from ...constants import NEWRL_DB


def migrate():
    optimize_db()

def optimize_db():
    print('Passing optimize db migration')
    return
    # """Remove redundant columns for db size reduction"""
    # con = sqlite3.connect(NEWRL_DB)
    # cur = con.cursor()

    # try:
    #     cur.execute('ALTER TABLE receipts DROP COLUMN IF EXISTS included_block_index')    
    #     cur.execute('ALTER TABLE receipts DROP COLUMN IF EXISTS signature')    
    #     cur.execute('ALTER TABLE receipts DROP COLUMN IF EXISTS timestamp')    
    #     cur.execute('DROP INDEX IF EXISTS idx_receipts_block_index_hash')
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS timestamp')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS type')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS currency')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS fee')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS description')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS valid')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS specific_data')    
    #     cur.execute('ALTER TABLE transactions DROP COLUMN IF EXISTS signatures')    
    # except Exception as e:
    #     print('Error with migration ', str(e))

    # con.commit()
    # con.close()
    
    # try:
    #     con = sqlite3.connect(NEWRL_DB)
    #     cur = con.cursor()
    #     cur.execute('VACUUM')
    #     con.commit()
    #     con.close()
    # except Exception as e:
    #     print('Error with migration ', str(e))
