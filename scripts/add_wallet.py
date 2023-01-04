import requests


NODE_URL = 'http://archive1-testnet1.newrl.net:8421'
CUSTODIAN_WALLET = { "public": "51017a461ecccdc082a49c3f6e17bb9a6259990f6c4d1c1dbb4e067878ddfa71cb4afbe6134bad588395edde20b92c6dd5abab4108d7e6aeb42a06229205cabb", "private": "92a365e63db963a76c0aa1389aee1ae4d25a4539311595820b295d3a77e07618", "address": "0x1342e0ae1664734cbbe522030c7399d6003a07a8" }


def add_wallet(public_key):
  add_wallet_request = {
    "custodian_address": CUSTODIAN_WALLET['address'],
    "ownertype": "1",
    "jurisdiction": "910",
    "kyc_docs": [
      {
        "type": 1,
        "hash": ""
      }
    ],
    "specific_data": {},
    "public_key": public_key
  }

  response = requests.post(NODE_URL + '/add-wallet', json=add_wallet_request)

  unsigned_transaction = response.json()
  unsigned_transaction['transaction']['fee'] = 1000000

  response = requests.post(NODE_URL + '/sign-transaction', json={
  "wallet_data": CUSTODIAN_WALLET,
  "transaction_data": unsigned_transaction
  })

  signed_transaction = response.json()

  print('signed_transaction', signed_transaction)
  print('Sending wallet add transaction to chain')
  response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
  print('Got response from chain\n', response.text)
  assert response.status_code == 200

public_key = input('Enter public key[leave blank to create new key pair]: ')

if public_key == '':
  response = requests.get(NODE_URL + '/generate-wallet-address')
  wallet = response.json()
  print('New wallet\n', wallet, '\n')
  public_key = wallet['public']

add_wallet(public_key)
