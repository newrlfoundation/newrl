import json
import sqlite3

from ..constants import NEWRL_DB


def migrate_state(state_file_name):
  con = sqlite3.connect(NEWRL_DB)

  cur = con.cursor()

  with open(state_file_name, 'r') as read_file:
    state_data = json.load(read_file)
    print(state_data)

  for wallet in state_data['all_wallets']:
    kyc_docs = []
    for doc_hash in wallet['kyc_doc_hashes']:
      kyc_docs.append({
        'type': 1, 'hash': doc_hash,
      })
    kyc_docs = json.dumps(kyc_docs)
    db_wallet_data = (wallet['wallet_address'], wallet['wallet_public'], wallet['custodian_wallet'], kyc_docs, wallet['ownertype'], wallet['jurisd'])
    cur.execute(f'''INSERT OR IGNORE INTO wallets
            (wallet_address, wallet_public, custodian_wallet, kyc_docs, owner_type, jurisdiction)
            VALUES (?, ?, ?, ?, ?, ?)''', db_wallet_data)

  for token in state_data['all_tokens']:
    token_attributes = json.dumps(token['token_attributes']) if 'token_attributes' in token else ''
    db_token_data = (token['tokencode'], token['tokenname'], token['tokentype'], token['first_owner'], token['custodian'], token['legaldochash'], token['amount_created'], token['sc_flag'], token_attributes)
    cur.execute(f'''INSERT OR IGNORE INTO tokens
    (tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, amount_created, sc_flag, token_attributes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', db_token_data)

  for balance in state_data['all_balances']:
    db_balance_data = (balance['wallet_address'], balance['tokencode'], balance['balance'])
    cur.execute(f'''INSERT OR REPLACE INTO balances
        (wallet_address, tokencode, balance) VALUES (?, ?, ?)''', db_balance_data)

  con.commit()
  con.close()

import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        migrate_state(sys.argv[1])
    else:
        print('Filename not provided')
