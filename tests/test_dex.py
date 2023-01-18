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

    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + '/get-wallet?wallet_address=' + wallet['address'])
    assert response.status_code == 200

    print("Wallet created with address "+wallet['address'])
    print('Test passed.')
    return wallet


def transfer_unilateral(from_wallet, to_wallet, token, amount):
    token_code = token['tokencode']
    req = {
        "transfer_type": 5,
        "asset1_code": token_code,
        "asset2_code": "",
        "wallet1_address": from_wallet['address'],
        "wallet2_address": to_wallet['address'],
        "asset1_qty": amount,
        "description": "",
        "additional_data": {}
    }
    response = requests.post(NODE_URL + '/add-transfer', json=req)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": from_wallet,
        "transaction_data": unsigned_transaction
    })
    signed_transaction = response.json()
    response = requests.post(
        NODE_URL + '/validate-transaction', json=signed_transaction)

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token_code}&wallet_address={to_wallet['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == amount


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
    unsigned_transaction['transaction']['fee'] = 1000000
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

def get_dex_datails():
    pool_token1_code = "nINR"+str(random.randrange(111111, 999999, 5))
    pool_token2_code = "nUSDC"+str(random.randrange(111111, 999999, 5))
    pool_ratio = "1:4"
    pool_fee = 0.005
    ot_token_code = "LPT_"+str(random.randrange(111111, 999999, 5))
    ot_token_name = ot_token_code
    
    wallet1 = create_wallet()
    wallet1_token1_init_amount = 10000
    wallet1_token2_init_amount = 40000

    wallet2 = create_wallet()
    wallet2_token1_init_amount = 1000
    wallet2_token2_init_amount = 7000

    #fund newrl for fee
    transfer_unilateral(WALLET,wallet1,{"tokencode":"NWRL"},10000000)
    transfer_unilateral(WALLET, wallet2, {"tokencode": "NWRL"}, 10000000)

    # fund wallet1
    create_token(WALLET, wallet1['address'], pool_token1_code,
                pool_token1_code, wallet1_token1_init_amount)
    create_token(WALLET, wallet1['address'], pool_token2_code,
                pool_token2_code, wallet1_token2_init_amount)

    #fund wallet2
    create_token(WALLET, wallet2['address'],
                pool_token1_code, pool_token1_code, wallet2_token1_init_amount)
    create_token(WALLET, wallet2['address'],
                pool_token2_code, pool_token2_code, wallet2_token2_init_amount)

    dex_details = {
        "pool_token1_code": pool_token1_code,
        "pool_token2_code": pool_token2_code,
        "pool_ratio": pool_ratio,
        "pool_fee": pool_fee,
        "ot_token_code": ot_token_code,
        "ot_token_name": ot_token_name,
        "wallet1" : wallet1,
        "wallet1_token1_init_amount": wallet1_token1_init_amount,
        "wallet1_token2_init_amount": wallet1_token2_init_amount,
        "wallet2": wallet2,
        "wallet2_token1_init_amount": wallet2_token1_init_amount,
        "wallet2_token2_init_amount": wallet2_token2_init_amount
         }
    return dex_details

def test_create_dex(request):
    dex_details = get_dex_datails()
    request.config.cache.set('dex_details', dex_details)
    pool_token1_code = dex_details["pool_token1_code"]
    pool_token2_code = dex_details["pool_token2_code"]
    pool_ratio = dex_details["pool_ratio"]
    pool_fee = dex_details["pool_fee"]
    ot_token_code = dex_details["ot_token_code"]
    ot_token_name = dex_details["ot_token_name"]

    wallet1 = dex_details["wallet1"]
    wallet1_token1_init_amount = dex_details["wallet1_token1_init_amount"]
    wallet1_token2_init_amount = dex_details["wallet1_token1_init_amount"]

    wallet2 = dex_details["wallet2"]
    wallet2_token1_init_amount = dex_details["wallet2_token1_init_amount"]
    wallet2_token2_init_amount = dex_details["wallet2_token1_init_amount"]

    response_ct_add = requests.get(NODE_URL+"/generate-contract-address")
    assert response_ct_add.status_code == 200
    ct_address = response_ct_add.json()
    response = requests.post(NODE_URL+'/add-sc', json=
        {
            "sc_address": ct_address,
            "sc_name": "dex",
            "version": "1.0.0",
            "creator": WALLET['address'],
            "actmode": "hybrid",
            "signatories": {"initialise_liquidity": None, "provide_liquidity": None, "swap": None, "withdraw": None},
            "contractspecs": {
                "pool_token1_code": pool_token1_code,
                "pool_token2_code": pool_token2_code,
                "ot_token_code": ot_token_code,
                "ot_token_name": ot_token_name,
                "token_ratio": pool_ratio,
                "fee": pool_fee
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
    # contracts_in_state = next(
    #     x for x in contracts if x['address'] == ct_address)
    # contracts_in_state = False
    # for x in contracts:
    #     c = x['address']
    #     d= ct_address
    #     if c == d:
    #         contracts_in_state = True
    #         break
    # assert contracts_in_state 
    request.config.cache.set('dex_address', ct_address) 



def test_provide_initial_liquidity(request):
    
    dex_details = request.config.cache.get('dex_details', None)
    dex_address = request.config.cache.get('dex_address',None)
    pool_token1_code = dex_details["pool_token1_code"]
    pool_token2_code = dex_details["pool_token2_code"]
    pool_ratio = dex_details["pool_ratio"]
    pool_fee = dex_details["pool_fee"]
    ot_token_code = dex_details["ot_token_code"]
    ot_token_name = dex_details["ot_token_name"]

    wallet1 = dex_details["wallet1"]
    wallet1_token1_init_amount = dex_details["wallet1_token1_init_amount"]
    wallet1_token2_init_amount = dex_details["wallet1_token2_init_amount"]

    wallet2 = dex_details["wallet2"]
    wallet2_token1_init_amount = dex_details["wallet2_token1_init_amount"]
    wallet2_token2_init_amount = dex_details["wallet2_token2_init_amount"]

    token_1_lp = 1000
    token2_lp = 4000
    req_json = {
        "sc_address": dex_address,
        "function_called": "initialise_liquidity",
        "signers": [
            wallet1['address']
        ],
        "params": {
            "recipient_address": wallet1['address'],
            "value": [
                {
                    "token_code": pool_token1_code,
                    "amount": token_1_lp
                },
                {
                    "token_code": pool_token2_code,
                    "amount": token2_lp
                }
            ]
    }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet1,
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

    response_token1 = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": pool_token1_code,
        "wallet_address": wallet1['address']
    })
    assert response_token1.status_code == 200
    balance_token1_resp = response_token1.json()
    balance_token1 = balance_token1_resp['balance']
    assert balance_token1 == wallet1_token1_init_amount-token_1_lp

    response_token2 = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": pool_token2_code,
        "wallet_address": wallet1['address']
    })
    assert response_token2.status_code == 200
    balance_token2 = response_token2.json()['balance']
    assert balance_token2 == wallet1_token2_init_amount-token2_lp

    response_token_ot = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": ot_token_code,
        "wallet_address": wallet1['address']
    })
    assert response_token_ot.status_code == 200
    balance_token_ot = response_token_ot.json()['balance']
    assert balance_token_ot == 2000

    #TODO check contract balance

#TODO bug, connect validate method
def test_swap(request):
    
    token2_swaped = 200
    token1_given  = 47
    
    dex_details = request.config.cache.get('dex_details', None)
    dex_address = request.config.cache.get('dex_address', None)

    pool_token1_code = dex_details["pool_token1_code"]
    pool_token2_code = dex_details["pool_token2_code"]
    pool_ratio = dex_details["pool_ratio"]
    pool_fee = dex_details["pool_fee"]
    ot_token_code = dex_details["ot_token_code"]
    ot_token_name = dex_details["ot_token_name"]

    wallet1 = dex_details["wallet1"]
    wallet1_token1_init_amount = dex_details["wallet1_token1_init_amount"]
    wallet1_token2_init_amount = dex_details["wallet1_token2_init_amount"]

    wallet2 = dex_details["wallet2"]
    wallet2_token1_init_amount = dex_details["wallet2_token1_init_amount"]
    wallet2_token2_init_amount = dex_details["wallet2_token2_init_amount"]

    req_json = {
        "sc_address": dex_address,
        "function_called": "swap",
        "signers": [
            wallet2["address"]
        ],
        "params": {
            "recipient_address": wallet2["address"],
            "token_sent": {
                "token_code": pool_token2_code,
                "amount": token2_swaped
            },
            "token_asked": {
                "token_code": pool_token1_code
            },
            "value": [
                {
                    "token_code": pool_token2_code,
                    "amount": token2_swaped
                }
            ]
        }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

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

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response_token1 = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": pool_token1_code,
        "wallet_address": wallet2['address']
    })
    assert response_token1.status_code == 200
    balance_token1_resp = response_token1.json()
    balance_token1 = balance_token1_resp['balance']
    assert balance_token1 == wallet2_token1_init_amount+token1_given

    response_token2 = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": pool_token2_code,
        "wallet_address": wallet2['address']
    })
    assert response_token2.status_code == 200
    balance_token2 = response_token2.json()['balance']
    assert balance_token2 == wallet2_token2_init_amount-token2_swaped

    # TODO assert pool balances 


def test_withdraw(request):

    dex_details = request.config.cache.get('dex_details', None)
    dex_address = request.config.cache.get('dex_address', None)

    pool_token1_code = dex_details["pool_token1_code"]
    pool_token2_code = dex_details["pool_token2_code"]
    pool_ratio = dex_details["pool_ratio"]
    pool_fee = dex_details["pool_fee"]
    ot_token_code = dex_details["ot_token_code"]
    ot_token_name = dex_details["ot_token_name"]

    wallet1 = dex_details["wallet1"]
    wallet1_token1_init_amount = dex_details["wallet1_token1_init_amount"]
    wallet1_token2_init_amount = dex_details["wallet1_token2_init_amount"]

    wallet2 = dex_details["wallet2"]
    wallet2_token1_init_amount = dex_details["wallet2_token1_init_amount"]
    wallet2_token2_init_amount = dex_details["wallet2_token2_init_amount"]

    amount_to_withdraw = 1000
    req_json = {
        "sc_address": dex_address,
        "function_called": "withdraw",
        "signers": [
            wallet1['address']
        ],
        "params": {
            "recipient_address": wallet1['address'],
            "withdraw_amount": amount_to_withdraw,
            "value": [
                {
                    "token_code": ot_token_code,
                    "amount": amount_to_withdraw
                }
            ]
        }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet1,
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

    response_ot = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": ot_token_code,
        "wallet_address": wallet1['address']
    })
    assert response_ot.status_code == 200
    balance_ot_resp = response_ot.json()
    balance_ot = balance_ot_resp['balance']
    assert balance_ot == 1000

    #TODO check pool ot balance


