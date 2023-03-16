import logging
import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV


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

def create_token(wallet, owner , token_name,token_code, amount):
    response = requests.post(NODE_URL+'/add-token', json={
        "token_name": token_name,
        "token_code": token_code,
        "token_type": "1",
        "first_owner":owner,
        "custodian": wallet["address"],
        "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
        "amount_created": amount,
        "tokendecimal": 0,
        "disallowed_regions": [],
        "is_smart_contract_token": False,
        "token_attributes": {}
    })


    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

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
    
def test_create_alias_contract(request):
    
    response_ct_add = requests.get(NODE_URL+"/generate-contract-address")
    assert response_ct_add.status_code == 200
    ct_address = response_ct_add.json()
    response = requests.post(NODE_URL+'/add-sc', json=
        {
            "sc_address": ct_address,
            "sc_name": "alias",
            "version": "1.0.0",
            "creator": WALLET['address'],
            "actmode": "hybrid",
            "signatories": {"add_alias": None, "update_alias": None},
            "contractspecs": {
            },
            "legalparams": {}
        }

    )

    print(response.text)
    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000

    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0


    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = requests.post(NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    # response = requests.get(NODE_URL+'/download-state')
    # assert response.status_code == 200
    # state = response.json()

    # contracts = state['contracts']
    # # contracts_in_state = next(
    # #     x for x in contracts if x['address'] == ct_address)
    # contracts_in_state = False
    # for x in contracts:
    #     c = x['address']
    #     d= ct_address
    #     if c == d:
    #         contracts_in_state = True
    #         break
    # assert contracts_in_state 

    params = {
            'table_name': "contracts",
            'contract_address':ct_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0

    request.config.cache.set('alias_address', ct_address) 



def test_create_alias(request):
    alias_address = request.config.cache.get('alias_address', None)
    wallet = create_wallet()
    fund_wallet_nwrl(WALLET,wallet['address'],8000000)
    alias = "alias_"+ str(random.randrange(111111, 999999, 5))
    req_json = {
        "sc_address": alias_address,
        "function_called": "add_alias",
        "signers": [
            wallet['address']
        ],
        "params": {
            "alias": alias
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
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
    assert  response.json()['response']['valid']
    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)


    params = {
            'table_name': "alias",
            'contract_address': alias_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0
    assert alias == response_val["data"][0][0]

    request.config.cache.set('wallet1', wallet) 
    request.config.cache.set('alias1', alias) 


def test_add_alias_duplicate_fail(request):
    alias_address = request.config.cache.get('alias_address', None)
    wallet = create_wallet()
    fund_wallet_nwrl(WALLET,wallet['address'],9000000)
    alias = "alias_"+ str(random.randrange(111111, 999999, 5))
    req_json = {
        "sc_address": alias_address,
        "function_called": "add_alias",
        "signers": [
            wallet['address']
        ],
        "params": {
            "alias": alias
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
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
    assert  response.json()['response']['valid']
    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)


    params = {
            'table_name': "alias",
            'contract_address': alias_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0
    assert response_val["data"][1][0] == alias    
    time.sleep(2)

    #duplicate entry    
    req_json = {
        "sc_address": alias_address,
        "function_called": "add_alias",
        "signers": [
            wallet['address']
        ],
        "params": {
            "alias": alias
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
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
    assert not response.json()['response']['valid']

def test_update_alias(request):
    alias_address = request.config.cache.get('alias_address', None)
    wallet = request.config.cache.get('wallet1', None)
    alias1 = request.config.cache.get('alias1', None)
    alias_updated = alias1+"_updated"
    req_json = {
        "sc_address": alias_address,
        "function_called": "update_alias",
        "signers": [
            wallet['address']
        ],
        "params": {
            "alias": alias_updated
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
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
    assert  response.json()['response']['valid']
    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)


    params = {
            'table_name': "alias",
            'contract_address': alias_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0
    assert response_val["data"][0][0] == alias_updated
    request.config.cache.set('alias1', alias_updated) 


def test_update_alias_fail(request):
    alias_address = request.config.cache.get('alias_address', None)
    wallet = request.config.cache.get('wallet1', None)
    alias1 = request.config.cache.get('alias1', None)
    wallet2 = create_wallet()
    fund_wallet_nwrl(WALLET,wallet2['address'], 5000000)
    req_json = {
        "sc_address": alias_address,
        "function_called": "update_alias",
        "signers": [
            wallet2['address']
        ],
        "params": {
            "alias": alias1
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet2,
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
    assert not  response.json()['response']['valid']

def test_update_alias_fail(request):
    alias_address = request.config.cache.get('alias_address', None)
    wallet = request.config.cache.get('wallet1', None)
    alias1 = request.config.cache.get('alias1', None)
    wallet2 = create_wallet()
    fund_wallet_nwrl(WALLET,wallet2['address'], 5000000)
    req_json = {
        "sc_address": alias_address,
        "function_called": "update_alias",
        "signers": [
            wallet2['address']
        ],
        "params": {
            "alias": alias1
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet2,
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
    assert not  response.json()['response']['valid']    



def test_update_alias_duplicate_fail(request):
    alias_address = request.config.cache.get('alias_address', None)
    wallet = request.config.cache.get('wallet1', None)
    alias1 = request.config.cache.get('alias1', None)

    #duplicate entry    
    req_json = {
        "sc_address": alias_address,
        "function_called": "update_alias",
        "signers": [
            wallet['address']
        ],
        "params": {
            "alias": alias1
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet,
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
    assert not response.json()['response']['valid']
