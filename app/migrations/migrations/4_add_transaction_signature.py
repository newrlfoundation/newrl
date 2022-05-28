import sqlite3

from ...constants import NEWRL_DB


def migrate():
    print('Running migration ' + __file__)
    con = sqlite3.connect(NEWRL_DB)
    # con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS _transactions
                    (
                    transaction_code text PRIMARY KEY,
                    block_index integer,
                    timestamp text,
                    type integer,
                    currency text,
                    fee real,
                    description text,
                    valid integer,
                    specific_data text,
                    signatures text)
                    ''')
    
    cursor = cur.execute(f'''select transaction_code, block_index, timestamp, type, currency, fee, 
                description, valid, specific_data
                FROM transactions''').fetchall()
    for obj in cursor:
        cur.execute(f'''INSERT OR IGNORE INTO _transactions
				(transaction_code, block_index, timestamp, type, currency, fee, 
                description, valid, specific_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', obj)
    
    cur.execute('DROP TABLE transactions')
    cur.execute('ALTER TABLE _transactions RENAME TO transactions')
    con.commit()
    con.close()


if __name__ == '__main__':
    migrate()
