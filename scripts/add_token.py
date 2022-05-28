import requests

# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {
#   "public": "pEeY8E9fdKiZ3nJizmagKXjqDSK8Fz6SAqqwctsIhv8KctDfkJlGnSS2LUj/Igk+LwAl91Y5pUHZTTafCosZiw==",
#   "private": "x1Hp0sJzfTumKDqBwPh3+oj/VhNncx1+DLYmcTKHvV0=",
#   "address": "0x6e206561a7018d84b593c5e4788c71861d716880"
# }

# NODE_URL = 'http://localhost:8182'
NODE_URL = 'http://testnet.newrl.net:8182'
WALLET = {"public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==","private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=","address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}


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
