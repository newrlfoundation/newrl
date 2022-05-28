import sqlite3

from ...constants import NEWRL_DB


def migrate():
    print('Running migration ' + __file__)
    con = sqlite3.connect(NEWRL_DB)
    # con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS _tokens
                    (tokencode text NOT NULL PRIMARY KEY, 
                    tokenname text,
                    tokentype integer,
                    first_owner text,
                    custodian text,
                    legaldochash text,
                    amount_created integer,
                    sc_flag integer,
                    disallowed text,
                    parent_transaction_code text,
                    token_attributes text,
                    tokendecimal integer)
                    ''')
    
    token_cursor = cur.execute(f'''select tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
                amount_created, sc_flag, parent_transaction_code, token_attributes
                FROM tokens''').fetchall()
    for token in token_cursor:
        cur.execute(f'''INSERT OR IGNORE INTO _tokens
				(tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
                amount_created, sc_flag, parent_transaction_code, token_attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', token)
    
    cur.execute('DROP TABLE tokens')
    cur.execute('ALTER TABLE _tokens RENAME TO tokens')
    con.commit()
    con.close()


if __name__ == '__main__':
    migrate()
