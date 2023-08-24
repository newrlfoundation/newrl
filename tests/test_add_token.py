import random
import string
import time
import requests
import json

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV
from app.config.nvalues import ZERO_ADDRESS

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
    "token_update_type":2
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
    assert response.json()["response"]["valid"] == True

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
    "token_update_type":2
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
    "token_update_type":2
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

def test_create_more_nft_failure(custodian_wallet=WALLET):
    token = add_token(is_editable=False,is_nft=True, amount= 1)
    token_code = token['tokencode']
    # token2 = add_token(token_code_input= token_code,is_editable=False,is_nft=True)

    add_token_request = {
    "token_name": token_code,
    "token_code": token_code,
    "token_type": "721",
    "first_owner": WALLET['address'],
    "custodian": custodian_wallet['address'],
    "legal_doc": "",
    "amount_created": 1,
    "tokendecimal": 2,
    "disallowed_regions": [],
    "is_smart_contract_token": False,
    "token_attributes": {
    }
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

def test_create_more_amount_nft_failure(custodian_wallet=WALLET):
    # token = add_token(is_editable=False,is_nft=True)
    # token_code = token['tokencode']
    # token2 = add_token(token_code_input= token_code,is_editable=False,is_nft=True)

    token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    is_nft = True
 
    token_attributes = {
            "tat1":"tat1value"      
        }   

    add_token_request = {
    "token_name": token_code,
    "token_code": token_code,
    "token_type": "1",
    "first_owner": custodian_wallet['address'],
    "custodian": custodian_wallet['address'],
    "legal_doc": "",
    "amount_created": 100,
    "tokendecimal": 2,
    "disallowed_regions": [],
    "is_smart_contract_token": False,
    "token_attributes": token_attributes
    }

    if is_nft:
        add_token_request['token_type']=721

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

    response_data = response.json()['response']
    assert not response_data['valid']

# def test_add_amount_to_token():
#     token = add_token(is_editable=False)
#     token_code = token['tokencode']
#     wallet_other = create_wallet() 
#     fund_wallet_nwrl(WALLET,wallet_other['address'],10000000)
#     add_token_request = {
#         "token_name": token_code,
#         "token_code": token_code,
#         "token_type": "1",
#         "first_owner": wallet_other["address"],
#         "custodian": wallet_other["address"],
#         "legal_doc": "",
#         "amount_created": 1,
#         "tokendecimal": 2,
#         "disallowed_regions": [],
#         "is_smart_contract_token": False,
#         "token_update_type" : 1,
#         "token_attributes": {
#         }
#     }

#     response = requests.post(NODE_URL + '/add-token', json=add_token_request)
#     unsigned_transaction = response.json()
#     unsigned_transaction['transaction']['fee'] = 1000000

#     response = requests.post(NODE_URL + '/sign-transaction', json={
#         "wallet_data": wallet_other,
#         "transaction_data": unsigned_transaction
#     })

#     signed_transaction = response.json()

#     print('signed_transaction', signed_transaction)
#     response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
#     print(response.text)
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json['response']['valid'] == True
#     response = requests.get(NODE_URL + '/get-token?token_code=' + token_code)
#     assert response.status_code == 200

#     token = response.json()
#     assert token['tokencode'] == token_code


def add_token(wallet_to_credit=WALLET['address'], amount=100, custodian_wallet=WALLET,is_editable=True,is_nft = False):
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

    if is_nft:
        add_token_request['token_type']=721

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


def test_add_token_type3_add_modify(request,custodian_wallet=WALLET):
    token = add_token()
    token_code = token['tokencode']
    token_attributes_updated = {
        "tat1":"tat1valueUpdated",
        "editable":False
    }

    add_token_request = {
    "token_name": token_code,
    "token_code": token_code,
    "token_type": "1",
    "first_owner": WALLET['address'],
    "custodian": WALLET['address'],
    "legal_doc": "",
    "amount_created": 20,
    "tokendecimal": 2,
    "disallowed_regions": [],
    "is_smart_contract_token": False,
    "token_attributes": token_attributes_updated,
    "token_update_type":3
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
    assert response.json()["response"]["valid"] == True

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
    assert token['amount_created'] == 120
    print('Test passed.')



def test_add_token_type4_delete_attributes_fail_balances_available(request,custodian_wallet=WALLET):
    token = add_token()
    token_code = token['tokencode']
    token_attributes_updated = {
        "tat1":"tat1valueUpdated",
        "editable":False
    }

    add_token_request = {
    "token_code": token_code,
    "token_attributes": {},
    "token_update_type":4,
    "custodian": custodian_wallet["address"]
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
    assert response.json()["response"]["valid"] == False




def test_add_token_type4_delete_attributes(request,custodian_wallet=WALLET):
    token = add_token(amount= 100)

    token_code = token['tokencode']
    #burn tokens for attribute delete
    transfer_tokens(WALLET,ZERO_ADDRESS, 100, token_code)

    add_token_request = {
    "token_code": token_code,
    "token_attributes": {},
    "token_update_type":4,
    "custodian": custodian_wallet["address"]
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
    assert response.json()["response"]["valid"] == True

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + '/get-token?token_code=' + token_code)
    assert response.status_code == 200
    token = response.json()
    assert token['tokencode'] == token_code
    token_attributes  = token['token_attributes']
    assert token_attributes == None
    print('Test passed.')

def create_wallet():
    # def test_create_wallet():
    response = requests.get(NODE_URL+"/generate-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    assert wallet['address']
    assert wallet['public']
    assert wallet['private']

    response = requests.post(NODE_URL+'/add-wallet', json={
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
        "public_key": wallet['public']
    })

    print(response.text)
    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL+'/get-wallet',
                            params={'wallet_address': wallet['address']})
    assert response.status_code == 200
    print("Wallet created with address "+wallet['address'])
    print('Test passed.')
    return wallet



def fund_wallet_nwrl(wallet,address,amount):
    req ={
        "transfer_type": 5,
        "asset1_code": "NWRL",
        "asset2_code": "",
        "wallet1_address": wallet["address"],
        "wallet2_address": address,
        "asset1_qty": amount,
        "description": "",
        "additional_data": {}
    }
    response = requests.post(NODE_URL+'/add-transfer', json = req)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
        "transaction_data": unsigned_transaction
    })

    print("adding token")
    assert response.status_code == 200
    signed_transaction = response.json()
    print("signing tx")
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    print("validating tx")
    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response_token1 = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": "NWRL",
        "wallet_address": address
    })
    assert response_token1.status_code == 200
    balance_token1_resp = response_token1.json()
    balance_token1 = balance_token1_resp['balance']
    assert balance_token1 == amount


 
def transfer_tokens(wallet,address,amount, token_code):
    req ={
        "transfer_type": 5,
        "asset1_code": token_code,
        "asset2_code": "",
        "wallet1_address": wallet["address"],
        "wallet2_address": address,
        "asset1_qty": amount,
        "description": "",
        "additional_data": {}
    }
    response = requests.post(NODE_URL+'/add-transfer', json = req)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
        "transaction_data": unsigned_transaction
    })

    print("adding token")
    assert response.status_code == 200
    signed_transaction = response.json()
    print("signing tx")
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    print("validating tx")
    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    assert response.status_code == 200
    assert response.json()["response"]["valid"] == True

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)
