import time
import requests

from setup import NODE_URL, WALLET

def test_add_wallet():
    response = requests.get(NODE_URL + '/generate-wallet-address')
    wallet = response.json()
    print('New wallet\n', wallet, '\n')
    public_key = wallet['public']
    wallet_address = wallet['address']


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

    print('Waiting to mine block')
    time.sleep(35)

    response = requests.get(NODE_URL + '/get-wallet?wallet_address=' + wallet_address)
    assert response.status_code == 200
    wallet = response.json()
    assert wallet['wallet_address'] == wallet_address
    assert wallet['wallet_public'] == public_key

    print('Test passed.')


if __name__ == '__main__':
    test_add_wallet()