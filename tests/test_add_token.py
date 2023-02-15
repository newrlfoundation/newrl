import random
import string
import time
import requests
import json

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV

def test_add_token(request):
    token = add_token()
    request.config.cache.set('token_code', token['tokencode'])

def test_modify_token_attributes(request,custodian_wallet=WALLET):
    token_code = request.config.cache.get('token_code', None)
    token_attributes_updated = {
        "tat1":"tat1valueUpdated",
        "editable":False
    }
    add_token_request = {
    "token_code": token_code,
    "custodian": custodian_wallet['address'],
    "token_attributes": token_attributes_updated,
    "token_update":True
    }

    response = requests.post(NODE_URL + '/add-token', json=add_token_request)
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
    token_attributes  = json.loads(token['token_attributes'])
    assert token_attributes == token_attributes_updated
    print('Test passed.')

def test_modify_token_attributes_with_false_is_edit(request,custodian_wallet=WALLET):
    token_code = request.config.cache.get('token_code', None)
    token_attributes_updated = {
        "tat1":"tat1valueUpdated",
        "editable":True
    }
    add_token_request = {
    "token_code": token_code,
    "custodian": custodian_wallet['address'],
    "token_attributes": token_attributes_updated,
    "token_update":True
    }

    response = requests.post(NODE_URL + '/add-token', json=add_token_request)
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

    response_json = response.json()
    assert response_json['response']['valid'] == False

def test_modify_token_attributes_with_is_edit_not_present(request,custodian_wallet=WALLET):
    token = add_token(is_editable=False)
    token_code = token['tokencode']
    token_attributes_updated = {
        "tat1":"tat1valueUpdated",
        "editable":True
    }
    add_token_request = {
    "token_code": token_code,
    "custodian": custodian_wallet['address'],
    "token_attributes": token_attributes_updated,
    "token_update":True
    }

    response = requests.post(NODE_URL + '/add-token', json=add_token_request)
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

    response_json = response.json()
    assert response_json['response']['valid'] == False

def add_token(wallet_to_credit=WALLET['address'], amount=100, custodian_wallet=WALLET,is_editable=True):
    token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    if is_editable:
        token_attributes = {
            "tat1":"tat1value",
            "editable":True
        }
    else:
        token_attributes = {
            "tat1":"tat1value"      
        }   

    add_token_request = {
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
    "token_attributes": token_attributes
    }

    response = requests.post(NODE_URL + '/add-token', json=add_token_request)
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

# '{"status":"SUCCESS","response":{"valid":true,"msg":"Transaction economic validation successful","new_transaction":true}}'