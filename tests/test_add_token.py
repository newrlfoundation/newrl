import random
import string
import time
import requests
import json

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV

token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def test_add_token():
    add_token()

def add_token(wallet_to_credit=WALLET['address'], amount=100, custodian_wallet=WALLET):
    add_wallet_request = {
    "token_name": token_code,
    "token_code": token_code,
    "token_type": "1",
    "first_owner": wallet_to_credit,
    "custodian": custodian_wallet['address'],
    "legal_doc": "",
    "amount_created": amount,
    "tokendecimal": 2,
    "disallowed_regions": [],
    "is_smart_contract_token": False,
    "token_attributes": {}
    }

    response = requests.post(NODE_URL + '/add-token', json=add_wallet_request)
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": custodian_wallet,
        "transaction_data": unsigned_transaction
    })

    signed_transaction = response.json()

    print('signed_transaction', signed_transaction)
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    print(response.text)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + '/get-token?token_code=' + token_code)
    assert response.status_code == 200
    token = response.json()
    assert token['tokencode'] == token_code
    assert token['first_owner'] == wallet_to_credit
    assert token['amount_created'] == amount

    print('Test passed.')
    return token

