import json
import urllib3

# NODE_URL = 'http://testnet.newrl.net:8182'
NODE_URL = 'http://testnet.newrl.net:8090'
# NODE_URL = 'http://newrl.net:8090'
# WALLET = {    "public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==",    "private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=",    "address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}
WALLET = {        "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="    }

http = urllib3.PoolManager()

token_code = input('Enter token code: ')
amount = input('Issue amount: ')
first_owner = input('First owner[c for custodian]: ')

if first_owner == 'c':
  first_owner = WALLET['address']

add_token_request = {
  "token_name": token_code,
  "token_code": token_code,
  "token_type": "1",
  "first_owner": first_owner,
  "custodian": WALLET['address'],
  "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
  "amount_created": amount,
  "tokendecimal": 0,
  "disallowed_regions": [],
  "is_smart_contract_token": False,
  "token_attributes": {}
}

response = http.request('POST', NODE_URL + '/add-token', body=json.dumps(add_token_request), headers={'Content-Type': 'application/json'})

unsigned_transaction = json.loads(response.data)

payload = {
    "wallet_data": WALLET,
    "transaction_data": unsigned_transaction
}
response = http.request('POST', NODE_URL + '/sign-transaction', body=json.dumps(payload), headers={'Content-Type': 'application/json'})

signed_transaction = json.loads(response.data)

print('signed_transaction', signed_transaction)
print('Sending wallet add transaction to chain')
response = http.request('POST', NODE_URL + '/validate-transaction', body=json.dumps(signed_transaction), headers={'Content-Type': 'application/json'})
print('Got response from chain\n', response.data)
assert response.status == 200