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
    
def test_create_pledge_contract(request):
    
    response_ct_add = requests.get(NODE_URL+"/generate-contract-address")
    assert response_ct_add.status_code == 200
    ct_address = response_ct_add.json()
    request_create =        {
            "sc_address": ct_address,
            "sc_name": "PledgingContract",
            "version": "1.0.0",
            "creator": WALLET['address'],
            "actmode": "hybrid",
            "signatories": {
                "setup": WALLET['address'],
                "deploy": WALLET['address'],
                "create": WALLET['address'],
                "pledge_tokens": None,
                "pledge_request": None,
                "pledge_finalise": None,
                "unpledge_tokens": None,
                "default_tokens":None
            },
            "contractspecs": {
                        "custodian_address": WALLET['address']
            },
            "legalparams": {}
        }
    
    response = requests.post(NODE_URL+'/add-sc', json= request_create )

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
    params = {
            'table_name': "contracts",
            'contract_address':ct_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0

    request.config.cache.set('pledge_address', ct_address) 



def test_create_pledge_Req(request):
    pledge_address = request.config.cache.get('pledge_address', None)
    borrower_wallet = create_wallet()
    fund_wallet_nwrl(WALLET,borrower_wallet['address'],20000000)
    lender_wallet = create_wallet()
    fund_wallet_nwrl(WALLET,lender_wallet['address'],20000000)
    
    req_json = {
        "sc_address": pledge_address,
        "function_called": "pledge_request",
        "signers": [
            borrower_wallet['address'],
            WALLET['address']
        ],
        "params": {
             "tokens":[{
           "token_code":"NWRL",
           "amount":1000000
       }],
       "value":[{
           "token_code":"NWRL",
           "amount":1000000
       }],
       "lender":lender_wallet['address']
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data":borrower_wallet ,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    req_sign = {
        "wallet_data":WALLET, 
        "transaction_data": signed_transaction
    }
    signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json= req_sign)

    assert signed_transaction_response.status_code == 200
    signed_transaction = signed_transaction_response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 2


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
            'table_name': "pledge_ledger",
            'contract_address': pledge_address,
            'unique_column': 'borrower',
            'unique_value': borrower_wallet['address']
        }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0

    request.config.cache.set('borrower_wallet', borrower_wallet) 
    request.config.cache.set('lender_wallet', lender_wallet) 

def test_finalise_pledge_Req(request):
    pledge_address = request.config.cache.get('pledge_address', None)
    borrower_wallet = request.config.cache.get('borrower_wallet', None)
    lender_wallet = request.config.cache.get('lender_wallet', None)
    
    
    req_json = {
        "sc_address": pledge_address,
        "function_called": "pledge_finalise",
        "signers": [
            borrower_wallet['address'],
            lender_wallet['address'],
            WALLET['address']
        ],
        "params": {
             "borrower_wallet": borrower_wallet['address'],
             "token_code":"NWRL",
             "lender": lender_wallet['address'],
              "tokens":[{
                "token_code":"NWRL"
            }]
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data":borrower_wallet ,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    req_sign = {
        "wallet_data":WALLET, 
        "transaction_data": signed_transaction
    }
    signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json= req_sign)

    assert signed_transaction_response.status_code == 200
    signed_transaction = signed_transaction_response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 2

    req_sign = {
        "wallet_data":lender_wallet, 
        "transaction_data": signed_transaction
    }
    signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json= req_sign)

    assert signed_transaction_response.status_code == 200
    signed_transaction = signed_transaction_response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 3

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
            'table_name': "pledge_ledger",
            'contract_address': pledge_address,
            'unique_column': 'borrower',
            'unique_value': borrower_wallet['address']
        }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0
    assert response_val["data"][7] == 11


def test_unpledge(request):
    pledge_address = request.config.cache.get('pledge_address', None)
    borrower_wallet = request.config.cache.get('borrower_wallet', None)
    lender_wallet = request.config.cache.get('lender_wallet', None)
    
    
    req_json = {
        "sc_address": pledge_address,
        "function_called": "unpledge_tokens",
        "signers": [
            WALLET['address']
        ],
        "params": {
             "borrower_wallet": borrower_wallet['address'],
             "token_code":"NWRL",
             "lender": lender_wallet['address'],
              "tokens":[{
                "token_code":"NWRL",
                "amount":1000000
            }]
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data":WALLET ,
        "transaction_data": unsigned_transaction
    })

    assert signed_transaction_response.status_code == 200
    signed_transaction = signed_transaction_response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    # req_sign = {
    #     "wallet_data":lender_wallet, 
    #     "transaction_data": signed_transaction
    # }
    # signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json= req_sign)

    # assert signed_transaction_response.status_code == 200
    # signed_transaction = signed_transaction_response.json()
    # assert signed_transaction['transaction']
    # assert signed_transaction['signatures']
    # assert len(signed_transaction['signatures']) == 2

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
            'table_name': "pledge_ledger",
            'contract_address': pledge_address,
            'unique_column': 'borrower',
            'unique_value': borrower_wallet['address']
        }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0
    assert response_val["data"][7] == 2

def test_default(request):
    pledge_address = request.config.cache.get('pledge_address', None)
    borrower_wallet = request.config.cache.get('borrower_wallet', None)
    lender_wallet = request.config.cache.get('lender_wallet', None)
    
    
    req_json = {
        "sc_address": pledge_address,
        "function_called": "default_tokens",
        "signers": [
            WALLET['address']
        ],
        "params": {
             "borrower_wallet": borrower_wallet['address'],
             "token_code":"NWRL",
             "lender": lender_wallet['address']
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data":WALLET ,
        "transaction_data": unsigned_transaction
    })

    assert signed_transaction_response.status_code == 200
    signed_transaction = signed_transaction_response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    # req_sign = {
    #     "wallet_data":lender_wallet, 
    #     "transaction_data": signed_transaction
    # }
    # signed_transaction_response = requests.post(NODE_URL+'/sign-transaction', json= req_sign)

    # assert signed_transaction_response.status_code == 200
    # signed_transaction = signed_transaction_response.json()
    # assert signed_transaction['transaction']
    # assert signed_transaction['signatures']
    # assert len(signed_transaction['signatures']) == 2

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
            'table_name': "pledge_ledger",
            'contract_address': pledge_address,
            'unique_column': 'borrower',
            'unique_value': borrower_wallet['address']
        }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    assert len(response_val["data"]) > 0
    assert response_val["data"][7] == -1
