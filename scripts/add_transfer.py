import json
import requests

NODE_URL = 'http://archive1-testnet1.newrl.net:8421'
WALLET = { "public": "51017a461ecccdc082a49c3f6e17bb9a6259990f6c4d1c1dbb4e067878ddfa71cb4afbe6134bad588395edde20b92c6dd5abab4108d7e6aeb42a06229205cabb", "private": "92a365e63db963a76c0aa1389aee1ae4d25a4539311595820b295d3a77e07618", "address": "0x1342e0ae1664734cbbe522030c7399d6003a07a8" }

transfer_type = input('Enter transfer type[4 for bilateral, 5 for unilateral]: ')
wallet1 = input('Enter first wallet address[leave blank for custodian]: ')
token1 = input('Enter first token code: ')
amount1 = input('Enter amount of first token: ')
wallet2 = input('Enter second wallet address: ')

if wallet1 == '':
  wallet1 = WALLET["address"]

if transfer_type == '4':
  token2 = input('Enter second token code: ')
  amount2 = input('Enter amount of second token: ')
else:
  token2 = ''
  amount2 = 0

add_transfer_request = {
  "transfer_type": int(transfer_type),
  "asset1_code": token1,
  "asset2_code": token2,
  "wallet1_address": wallet1,
  "wallet2_address": wallet2,
  "asset1_qty": int(amount1),
  "asset2_qty": int(amount2),
  "description": "",
  "additional_data": {}
}

print(add_transfer_request)

response = requests.post(NODE_URL + '/add-transfer', json=add_transfer_request)

unsigned_transaction = response.json()
unsigned_transaction['transaction']['fee'] = 1000000
response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET,
    "transaction_data": unsigned_transaction
})
signed_transaction = response.json()

# Transfer type 4 need to be signed by both wallets
if transfer_type == '4':
  WALLET2 = input('Enter complete json for wallet2: ')
  WALLET2 = json.loads(WALLET2)

  response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET2,
    "transaction_data": signed_transaction
  })
  signed_transaction = response.json()

print('signed_transaction', signed_transaction)
response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
print(response.text)
print(response.status_code)
assert response.status_code == 200
