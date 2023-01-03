import requests


NODE_URL = 'http://archive1-testnet1.newrl.net:8421'
WALLET = { "public": "51017a461ecccdc082a49c3f6e17bb9a6259990f6c4d1c1dbb4e067878ddfa71cb4afbe6134bad588395edde20b92c6dd5abab4108d7e6aeb42a06229205cabb", "private": "92a365e63db963a76c0aa1389aee1ae4d25a4539311595820b295d3a77e07618", "address": "0x1342e0ae1664734cbbe522030c7399d6003a07a8" }

token_code = input('Enter token code: ')
amount = input('Issue amount: ')
first_owner = input('First owner[leave blank for custodian]: ')

if first_owner == '':
  first_owner = WALLET['address']

add_wallet_request = {
  "token_name": token_code,
  "token_code": token_code,
  "token_type": "1",
  "first_owner": first_owner,
  "custodian": WALLET['address'],
  "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
  "amount_created": amount,
  "tokendecimal": 2,
  "disallowed_regions": [],
  "is_smart_contract_token": False,
  "token_attributes": {}
}

response = requests.post(NODE_URL + '/add-token', json=add_wallet_request)

unsigned_transaction = response.json()

unsigned_transaction['transaction']['trans_code'] = unsigned_transaction['transaction']['trans_code'] + '1'
unsigned_transaction['transaction']['fee'] = 1000000

response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET,
    "transaction_data": unsigned_transaction
})

signed_transaction = response.json()

print('signed_transaction', signed_transaction)
response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
print(response.text)
print(response.status_code)
assert response.status_code == 200
