import requests

NODE_URL = 'http://testnet.newrl.net:8182'
# NODE_URL = 'http://localhost:8182'
WALLET = {"public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==","private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=","address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}

# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {"address": "0xc29193dbab0fe018d878e258c93064f01210ec1a","public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==","private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="}


# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {
#   "public": "pEeY8E9fdKiZ3nJizmagKXjqDSK8Fz6SAqqwctsIhv8KctDfkJlGnSS2LUj/Igk+LwAl91Y5pUHZTTafCosZiw==",
#   "private": "x1Hp0sJzfTumKDqBwPh3+oj/VhNncx1+DLYmcTKHvV0=",
#   "address": "0x6e206561a7018d84b593c5e4788c71861d716880"
# }

def add_wallet(public_key):
  add_wallet_request = {
    "custodian_address": WALLET['address'],
    "ownertype": "1",
    "jurisdiction": "910",
    "kyc_docs": [
  {
    "type": 1,
    "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
  }
    ],
    "specific_data": {},
    "public_key": public_key
  }

  response = requests.post(NODE_URL + '/add-wallet', json=add_wallet_request)

  unsigned_transaction = response.json()

  response = requests.post(NODE_URL + '/sign-transaction', json={
  "wallet_data": WALLET,
  "transaction_data": unsigned_transaction
  })

  signed_transaction = response.json()

  # print('signed_transaction', signed_transaction)
  print('Sending wallet add transaction to chain')
  response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
  print('Got response from chain\n', response.text)
  assert response.status_code == 200

for public_key in ['PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==', 'FbSwBu4b9aD3JoAaI1IzzWPtEvWiGSn6dIB1cm8h8NZlF4cQrGyESEdVGxS5tebWcalnyFSGjasnEPlyS45SAg==', 'bNSqzHBCK4tnf7rB780eF+Exph0ZCY1Vu2jnBPHq1zw2AIun4aar+vgHmUj8AY4oLF7iWfpBgkkVuHe6L1jepA==', 'KFYSB5fh0dASPz1lSys9DdkMl3Ouukydn6qpo32syTVoYkA5WYhSVCkp9kibr+Lgnw8DkOkAq5CCfP0CopiGHw==', 'Q0sw+ELDy7xWPbi3/1P0KaaYqeLkc97GEsoLumDuAAbAf1i2kNl2pYROY5sFVtmIUAtL4wUP6xoWZhIrcw4LrA==', 'ROSUDqyRFB6ZaHqQFsv5uUfx6GKUNZvpqsFNV/Gvv6Mjw1i+DTpUeFnj7qkKrMwjKZCJVdbRY+5e+Va0i2UGJw==', 'beUpeaiKW4CxBaGSYKCFYEG/f+PvFiS3H3l53OTqFoBpC7Bh1oEJz4QZ0Z1VkIBpXUw8ZcBwdBVLtr04GS/ltg==', 'Z5o1TBi438TSLd/PH1Qv7zIh8Dsx7f/siJXsnQcrEjCI8Pd70FvcMA4nPwQzreusQ6WBhvL1bmgtwx7VEZH5rA==', '4CscAOY/km2vv+5gkr8bVDb+1Po9oCWGHx3PkxBKNzadrDgPpYOJ/IaP65jgi48PQb46njNTbXhbc7ivKnt6lA==', 'KSnHvsppFRdKlQe0YbImp2Ipl3+SO1h7nlGunIB52OlydliOGggcNDtM8ZF0tDk8Fq/NxlhCTZuvVUrGwtRdkw==', 'gBqrxVsPlP/NSZFTHrozyGnp0wucGhJHOlDfefF3Q9WaGqkZWZr5RKPCOjmmKdEs3ohra39LYsGhexXjhZS7lw==', 'PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==']:
  add_wallet(public_key)
