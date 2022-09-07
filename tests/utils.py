import requests
import time
from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV

def sign_and_wait_mine(unsigned_transaction):
    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET,
    "transaction_data": unsigned_transaction
    })

    signed_transaction = response.json()

    print('signed_transaction', signed_transaction)
    print('Sending wallet add transaction to chain')
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    print('Got response from chain\n', response.text)
    assert response.json()['response']['valid']

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)