import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME

token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def test_add_token():
    add_wallet_request = {
    "token_name": token_code,
    "token_code": token_code,
    "token_type": "1",
    "first_owner": WALLET['address'],
    "custodian": WALLET['address'],
    "legal_doc": "",
    "amount_created": 1000,
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
    assert response.status_code == 200

    print('Waiting to mine block')
    time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + '/get-token?token_code=' + token_code)
    assert response.status_code == 200
    token = response.json()
    assert token['tokencode'] == token_code
    assert token['first_owner'] == WALLET['address']
    assert token['amount_created'] == 1000

    print('Test passed.')


if __name__ == '__main__':
    test_add_token()