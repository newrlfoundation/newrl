import json
import requests
import urllib3

# NODE_URL = 'http://localhost:8182'
NODE_URL = 'http://testnet.newrl.net:8182'
WALLET = {"public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==","private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=","address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}

# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {"address": "0xc29193dbab0fe018d878e258c93064f01210ec1a","public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==","private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="}

contract_address = input('Enter Contract address: ')


req = {
  "sc_address": contract_address,
  "function_called": "deploy",
  "signers": [
    WALLET['address']
  ],
  "params": {
    "sender": WALLET['address']
  }
}

print(json.dumps(req))
response = requests.post(NODE_URL + '/call-sc', json=req)
print(response.text)
unsigned_transaction = response.json()

response = requests.post(NODE_URL + '/sign-transaction', json={
"wallet_data": WALLET,
"transaction_data": unsigned_transaction
})

signed_transaction = response.json()
print('signed_transaction', signed_transaction)
print('Sending contract call transaction to chain')
response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
print('Got response from chain\n', response.text)
assert response.status_code == 200
