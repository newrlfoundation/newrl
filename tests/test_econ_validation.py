import time
import requests
import random
import string

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV
STAKE_CT_ADDRESS = 'ct1111111111111111111111111111111111111115'

def add_token(wallet_to_credit=WALLET['address'], amount=100, custodian_wallet=WALLET, 
    fee_payer_wallet=None, skip_custodian_sign=False, skip_fee_payer_sign=False):
    token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
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
    if fee_payer_wallet is not None:
        unsigned_transaction['transaction']['fee_payer'] = fee_payer_wallet['address']

    if not skip_custodian_sign:
        response = requests.post(NODE_URL + '/sign-transaction', json={
            "wallet_data": custodian_wallet,
            "transaction_data": unsigned_transaction
        })

        signed_transaction = response.json()
    else:
        signed_transaction = unsigned_transaction

    if fee_payer_wallet is not None and not skip_fee_payer_sign:
        response = requests.post(NODE_URL + '/sign-transaction', json={
            "wallet_data": fee_payer_wallet,
            "transaction_data": signed_transaction
        })

        signed_transaction = response.json()
        # assert len(signed_transaction['signatures']) == 2

    print('signed_transaction', signed_transaction)
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    print(response.text)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    return token_code


def check_token_present(token_code, should_fail=False):
    response = requests.get(NODE_URL + '/get-token?token_code=' + token_code)
    if should_fail:
        assert response.status_code == 400
    else:
        assert response.status_code == 200


def test_econ_type_1_create_wallet():
    w1 = add_wallet()
    response = requests.get(NODE_URL + '/generate-wallet-address')
    w2 = response.json()
    print('New wallet\n', w2, '\n')
    public_key = w2['public']
    wallet_address = w2['address']

    fund_wallet_nwrl(WALLET,w1['address'],8000000)

    add_wallet_request = {
        "custodian_address": w1['address'],
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
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": w1,
    "transaction_data": unsigned_transaction
    })

    signed_transaction = response.json()

    print('signed_transaction', signed_transaction)
    print('Sending wallet add transaction to chain')
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    print('Got response from chain\n', response.text)
    response_data = response.json()['response']
    assert not response_data['valid']
    assert response_data['msg'] == ["Invalid custodian wallet"]
    

def test_econ_type_2_token_creation():
    response = requests.get(NODE_URL + '/generate-wallet-address')
    wallet = response.json()
    print('New wallet\n', wallet, '\n')
    wallet_address = wallet['address']

    token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    

    token_attributes = {
            "tat1":"tat1value",
            "editable":True
        }
 
    add_token_request = {
    "token_name": token_code,
    "token_code": token_code,
    "token_type": "1",
    "first_owner": wallet_address,
    "custodian": WALLET['address'],
    "legal_doc": "",
    "amount_created": 2000000,
    "tokendecimal": 2,
    "disallowed_regions": [],
    "is_smart_contract_token": False,
    "token_attributes": token_attributes
    }

    response = requests.post(NODE_URL + '/add-token', json=add_token_request)
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": unsigned_transaction
    })

    signed_transaction = response.json()

    print('signed_transaction', signed_transaction)
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    response_data = response.json()['response']
    assert not response_data['valid']
    assert response_data['msg'] == ["No first owner address found"]


def test_econ_type_3_sc_value_no_balance():
    wallet1 = add_wallet()
    fund_wallet_nwrl(WALLET,wallet1['address'],2000000)

    sc_address = STAKE_CT_ADDRESS
    req_json = {
        "sc_address": sc_address,
        "function_called": "stake_tokens",
        "signers": [
            wallet1['address']
        ],
        "params": {
                "token_amount":9000000000,
                "wallet_address": wallet1['address'],
                "value": [
                    {
                        "token_code": "NWRL",
                        "amount": 9000000000,
                    }
                ]
            }
    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

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
    response_data = response.json()['response']
    assert not response_data['valid']
    assert response_data['msg'] == ['Invalid balance in value']
    


def test_econ_type_5_transfer_invalid_recipient():
    token_code = 'TOKEN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    response = requests.get(NODE_URL + '/generate-wallet-address')
    wallet = response.json()
    print('New wallet\n', wallet, '\n')
    rndm_wallet_address = wallet['address']

    req ={
        "transfer_type": 5,
        "asset1_code": "NWRL",
        "asset2_code": "",
        "wallet1_address": WALLET['address'],
        "wallet2_address": rndm_wallet_address,
        "asset1_qty": 500,
        "description": "",
        "additional_data": {}
    }
    response = requests.post(NODE_URL + '/add-transfer', json=req)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000
    
    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET,
    "transaction_data": unsigned_transaction
    })
    signed_transaction = response.json()
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    response_data = response.json()['response']
    assert not response_data['valid']
    assert response_data['msg'] == ['Invalid sender2 wallet']

# def test_econ_type_5_transfer_invalid_balance():
#     token_code = 'TOKEN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

#     response = requests.get(NODE_URL + '/generate-wallet-address')
#     wallet = response.json()
#     print('New wallet\n', wallet, '\n')
#     rndm_wallet_address = wallet['address']

#     req ={
#         "transfer_type": 5,
#         "asset1_code": "NWRL",
#         "asset2_code": "",
#         "wallet1_address": WALLET['address'],
#         "wallet2_address": rndm_wallet_address,
#         "asset1_qty": 990000000000000000000d0,
#         "description": "",
#         "additional_data": {}
#     }
#     response = requests.post(NODE_URL + '/add-transfer', json=req)

#     assert response.status_code == 200
#     unsigned_transaction = response.json()
#     unsigned_transaction['transaction']['fee'] = 1000000
    
#     response = requests.post(NODE_URL + '/sign-transaction', json={
#     "wallet_data": WALLET,
#     "transaction_data": unsigned_transaction
#     })
#     signed_transaction = response.json()
#     response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
#     response_data = response.json()['response']
#     assert not response_data['valid']
#     assert response_data['msg'] == ['Invalid sender2 wallet']

# def test_econ_type_5_transfer_invalid_tokens():
#     w1 = add_wallet()
#     wallet_address = w1['address']


#     add_wallet_request = {
#         "custodian_address": w1['address'],
#         "ownertype": "1",
#         "jurisdiction": "910",
#         "kyc_docs": [
#     {
#         "type": 1,
#         "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
#     }
#         ],
#         "specific_data": {},
#         "public_key": public_key
#     }

#     response = requests.post(NODE_URL + '/add-wallet', json=add_wallet_request)

#     unsigned_transaction = response.json()
#     unsigned_transaction['transaction']['fee'] = 1000000

#     response = requests.post(NODE_URL + '/sign-transaction', json={
#     "wallet_data": WALLET,
#     "transaction_data": unsigned_transaction
#     })

#     signed_transaction = response.json()

#     print('signed_transaction', signed_transaction)
#     print('Sending wallet add transaction to chain')
#     response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
#     print('Got response from chain\n', response.text)
#     assert response.status_code == 200   


# def test_econ_type_6_trust_invalid_pids():
#     w1 = add_wallet()
#     response = requests.get(NODE_URL + '/generate-wallet-address')
#     wallet = response.json()
#     print('New wallet\n', wallet, '\n')
#     public_key = wallet['public']
#     wallet_address = wallet['address']


#     add_wallet_request = {
#         "custodian_address": w1['address'],
#         "ownertype": "1",
#         "jurisdiction": "910",
#         "kyc_docs": [
#     {
#         "type": 1,
#         "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
#     }
#         ],
#         "specific_data": {},
#         "public_key": public_key
#     }

#     response = requests.post(NODE_URL + '/add-wallet', json=add_wallet_request)

#     unsigned_transaction = response.json()
#     unsigned_transaction['transaction']['fee'] = 1000000

#     response = requests.post(NODE_URL + '/sign-transaction', json={
#     "wallet_data": WALLET,
#     "transaction_data": unsigned_transaction
#     })

#     signed_transaction = response.json()

#     print('signed_transaction', signed_transaction)
#     print('Sending wallet add transaction to chain')
#     response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
#     print('Got response from chain\n', response.text)
#     assert response.status_code == 200   

def add_wallet():
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
    unsigned_transaction['transaction']['fee'] = 1000000

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

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + '/get-wallet?wallet_address=' + wallet_address)
    assert response.status_code == 200
    _wallet = response.json()
    assert _wallet['wallet_address'] == wallet_address
    assert _wallet['wallet_public'] == public_key

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
    