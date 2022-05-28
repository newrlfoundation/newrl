import requests

NODE_URL = 'http://testnet.newrl.net:8182'
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

# for public_key in ['PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==', '6YCLRYLmn7xLEZoBnvFVAhqMs0RSLHh6qx4+FMFaMhc2vSDh9pxpdLQdjUSPb/JgFsA25Wpkh5r9myC0HbkaOQ==', 'BZdhXCER0+foqtVOjzfXVi6bE33oS+F7QybRgAKKNG955iIZymjEYZE8RDSKwHI1Ww0iMkaZ6a63ZVR6Q2ZOsw==', 'F4JyBkTigIviJ2ZXBDED38bwi3nKiq8NEyxFlYtmcPB0siRSIBRBpMSzdAU9hdmXodSapJcoO/lhhwlZP413CA==', 'FVatd42BznwblvNFBET9neGXHazylhevWEZX3R0OAKjpaJciUDz0AVHta6BcZrSMcelYrI/wE0HP9tLGbAgwnQ==', 'NLvTGkixKssh3NQB5Jht4pQIiYxJBw/8WYLQ7uwH7EWdO1UlPHSewrIRvPTeEmmrlpa/AmdRvh/6hkbfhZRmYg==', 'K7RISj43N9umd+rP/zarVPmUsH/4MQjukYaZeG81nIt8q2RvJaoTOPNVJRmfMHEvpzMWnD4kil7D4zN84cHloA==', 'qyMa3ncG6xzoOulTfWp1Dbf06yKGo728yqYZctWNCR21NxuCVEoUDCPR99CxEvHBhE7SbUTiLe289jpF52qh7g==', 'hKpfJMvMoOMWvONGJOV9ncQmtupushRNKgYkNLxfnU+1ZnX/XYDZT5ly6oaSypn6fQxtgJFLaHeSSvkZKq0RfA==', 'J8Xy8uUw5AlFGkB9zlLhElVXPstVsbo9V70hqVes6tPJSOspAC+v+2p9HZNESnVQaiXznXkP24rHkz/IoamCmw==', '74ZxEE/N6SUh6PW6erTWkBI4insFRli8XURit0EnTUYU1B36RoQRAFU4egQkJr/WgcJd1SZErqtPpxLn2FzSfA==', 'qcFAa8JxDAubyEjHz2xlkE22GhhPE2HIOxwlna1DfNvtCxPc+D0eK3DHXyvcAuqGgpGhi8baftOkw7He2SqyHw==', 'SG8cb1OTYpbqi230dLn8QN5CLNFnE+ZsjJKhHBGZjHExsnJ3RJ44IhUzU3/+RnGThLd/i4IkRaB0Eic0YSIiXw==', '8nkFblwk1Jq4frQURGvW36/1qHw5MhGv2A1RHnjhtdddAavfLEtO6Dq64MwXqWAy1XN+Wx4wWfztgNv9pdkh4A==', 'pzg0Ms3/R+13KIB/gIrUsISmc5jC/OqhJIJrfy0h4ggodEpiHZsWSRsEF0hZl1HCBOVLUq01jKIZFVZZ9uV8aw==', '+1pc+A8bYWfkiOuPv3XMXzJ3xs2TR6lVwHIfkzJfBYiGxKnNhT2IyRxbjlZshlSgmQEhxB+k7PraaBPdN5d7Wg==', 'JSDoAwJQqmFNVls09fVzcqtAROhh29tLDEXmLqs4ndpCmVdv0kHslX/DhFFq8BFuSv8nfb9uaWfZ9crpFNsDhg==', 'Vhl+eXpXDoc2bgO0IG+wQ+DfOSIQPerEIdXA1N7mDzuUccLHvQEmeho0uk0ormbuwAcHR/nYgK7I3LoCPuNOmA==', 'lrjRgzFVALEP2W52LeflWA2zV5hOxPiKgkJiXSD9IC1PxJShwpQbF8oz0Y6SzowBILH3MXOusiFIl4+EUMsm8Q==', 'Bw6baJzl+Z6yJATcWgd+xVzv2UrfkvMP6STN+TgYevg0gYJGDKjLi4Vr+Gf6Ps3FACcVk26dEjSAuFtHHnodFg==', 'zZuUGV7BMXRVRwo+S1mPWxLuyaSLUCYpEhiTxoX0jR+lNBcC4BSivjkRbeJj6f7/c3iRAy4B9BSTGhI2azMuZA==', '0FKo0JWB+TZa9BN/WoBkK5hqjiDvgnlgF6ONr9m5+ebG9aY1Uz+wVyucbJTdHwyq0xYVjYIoZeL6TEw4lvNYlw==', '3kRKKSz6RxRAYTGdV6s7kMLBSYKuS2+prImkx3g1XBc0xtYQB/VW7cEgVf1DR7Fdn2P1AclESpokmGJK2OENWA==', 'yN4Iuk/sWqwkFn8+wtJuyCHKLWWIIOjwBjua7NFE4AKKIGqXLR2nOvhfkZCZ7DRyGLfAqzphcSYaoH2VNvLpUg==', 'PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==']:
#   add_wallet(public_key)
