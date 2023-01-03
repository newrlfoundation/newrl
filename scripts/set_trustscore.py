import requests


NODE_URL = 'http://archive1-testnet1.newrl.net:8421'
WALLET = { "wallet_here" }

TRUST_SCORE_DECIMAL = 10000

destination_wallet_address = input('Enter destination wallet address: ')
source_wallet_address = WALLET['address']
score = input('Enter score[-100 to 100]: ')
score = int(score)

trust_score_update_request = {
      "source_address": source_wallet_address,
      "destination_address": destination_wallet_address,
      "tscore": score * TRUST_SCORE_DECIMAL
  }
response = requests.post(NODE_URL + '/update-trustscore', json=trust_score_update_request)
unsigned_transaction = response.json()
unsigned_transaction['transaction']['fee'] = 1000000

# In production use Newrl sdk to sign offline
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
