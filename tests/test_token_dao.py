import logging
import random
import string
import time
import requests
import pytest

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

def get_pid(wallet):
    response = requests.get(
        NODE_URL+"/get-wallet", params={'wallet_address': wallet["address"]})
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["person_id"]
    return response_val["person_id"]

def create_token(wallet, owner, token_name, token_code, amount):
    response = requests.post(NODE_URL+'/add-token', json={
        "token_name": token_name,
        "token_code": token_code,
        "token_type": "1",
        "first_owner": owner,
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
    
def get_dao_details():
    wallet_founder1 = create_wallet()
    wallet_founder1_pid = get_pid(wallet_founder1)
    wallet_founder2 = create_wallet()
    wallet_founder2_pid = get_pid(wallet_founder2)
    wallet_founder3 = create_wallet()
    wallet_founder3_pid = get_pid(wallet_founder3)
    wallet_member1 = create_wallet()
    wallet_company_founder = create_wallet()
    company_token_name = "CMP_"+str(random.randrange(111111, 999999, 5))
    create_token(wallet_company_founder,
                wallet_company_founder["address"], company_token_name, company_token_name, 200)
    member_pid = get_pid(wallet_member1)
    wallet_dao = create_wallet()
    fund_wallet_nwrl(WALLET, wallet_founder1['address'], 20000000)
    fund_wallet_nwrl(WALLET, wallet_founder2['address'], 20000000)
    fund_wallet_nwrl(WALLET, wallet_founder3['address'], 20000000)
    fund_wallet_nwrl(WALLET, wallet_company_founder['address'], 20000000)

    dao_token_name = "dao_token"+str(random.randrange(111111, 999999, 5))
    dao_manager_address = "ct9000000000000000000000000000000000000da0"
    dao_name = "dao_token_"+str(random.randrange(111111, 999999, 5))
    dao_details = {
        'wallet_founder1': wallet_founder1,
        'wallet_founder1_pid' : wallet_founder1_pid,
        'wallet_founder2': wallet_founder2,
        'wallet_founder2_pid': wallet_founder2_pid,
        'wallet_founder3': wallet_founder3,
        'wallet_founder3_pid': wallet_founder3_pid,
        'wallet_member1': wallet_member1,
        'member_pid': member_pid,
        'wallet_dao': wallet_dao,
        'dao_token_name': dao_token_name,
        "dao_name": dao_name,
        "dao_manager_address" : dao_manager_address,
        "company_token_name": company_token_name,
        "wallet_company_founder": wallet_company_founder
        
    }

    return dao_details

def test_create_token_dao(request):
    dao_details = get_dao_details()
    request.config.cache.set('dao_details', dao_details)
    wallet_founder1 = dao_details["wallet_founder1"]
    wallet_founder2 = dao_details["wallet_founder2"]
    wallet_founder3 = dao_details["wallet_founder3"]
    dao_manager_address = dao_details["dao_manager_address"]
    dao_name = dao_details["dao_name"]
    dao_token_name = dao_details["dao_token_name"]

    response_ct_add = requests.get(NODE_URL+"/generate-contract-address")
    assert response_ct_add.status_code == 200
    ct_address = response_ct_add.json()
    print(wallet_founder1["address"])
    req_json = {
        "sc_address": dao_manager_address,
        "function_called": "create",
        "signers": [
            wallet_founder1['address']
        ],
        "params": {
            "dao_name": dao_name,
            "dao_address": ct_address,
            "founders": [
                wallet_founder1['address'],
                wallet_founder2['address'],
                wallet_founder3['address']
            ],
            "dao_main_sc": "token_fund_dao",
            "dao_main_sc_version": "1.0.0",
            "contractspecs": {
                "token_name": dao_token_name,
                "max_members": 999999999,
                "max_voting_time": 300000,
                "exchange_token_code": "NWRL",
                "exchange_rate": 2,
                "total_votes": 30,
                "signatories": {
                    "vote_on_proposal": None,
                    "delete_member": [
                        -1
                    ],
                    "create_proposal": None,
                    "add_member": [
                        -1
                    ],
                    "invest": [
                        -1
                    ],
                    "disburse":None,
                    "payout": [
                        -1
                    ],
                    "lock_tokens": None,
                    "issue_token": None
                },
                "voting_schemes": [
                    {
                        "function": "add_member",
                        "voting_scheme": "voting_scheme_one",
                        "params": {
                            "min_yes_votes": 50
                        }
                    },
                    {
                        "function": "delete_member",
                        "voting_scheme": "voting_scheme_one",
                        "params": {
                            "min_yes_votes": 50
                        }
                    },
                    {
                        "function": "invest",
                        "voting_scheme": "voting_scheme_one",
                        "params": {
                            "min_yes_votes": 50
                        }
                    },
                    {
                        "function": "payout",
                        "voting_scheme": "voting_scheme_one",
                        "params": {
                            "min_yes_votes": 50
                        }
                    }
                ]
            },
            "legalparams": {}
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json= req_json
    )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder1,
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

    response = requests.get(NODE_URL+'/download-state')
    assert response.status_code == 200
    state = response.json()

    contracts = state['contracts']
    contracts_in_state = False
    for x in contracts:
        c = x['address']
        d = ct_address
        if c == d:
            contracts_in_state = True
            break
    assert contracts_in_state
    request.config.cache.set('token_dao_address', ct_address)

def test_issue_dao_tokens(request):
    dao_details = request.config.cache.get('dao_details', None)
    wallet_founder1 = dao_details["wallet_founder1"]
    wallet_founder2 = dao_details["wallet_founder2"]
    wallet_founder3 = dao_details["wallet_founder3"]
    dao_token_name = dao_details["dao_token_name"]

    token_dao_address = request.config.cache.get('token_dao_address', None)

    # Issue to member1
    req = {
        "sc_address": token_dao_address,
        "function_called": "issue_token",
        "signers": [
            wallet_founder1['address']
        ],
        "params": {
            "value": [
                {
                    "token_code": "NWRL",
                    "amount": 20
                }],
            "recipient_address": wallet_founder1['address'],
            "amount": 10
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json= req
    )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder1,
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
    # Issue to member2
    req = {
        "sc_address": token_dao_address,
        "function_called": "issue_token",
        "signers": [
            wallet_founder2['address']
        ],
        "params": {
            "value": [
                {
                    "token_code": "NWRL",
                    "amount": 20
                }],
            "recipient_address": wallet_founder2['address'],
            "amount": 10
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder2,
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

    # # Issue to member3
    req = {
        "sc_address": token_dao_address,
        "function_called": "issue_token",
        "signers": [
            wallet_founder3['address']
        ],
        "params": {
            "value": [
                {
                    "token_code": "NWRL",
                    "amount": 20
                }],
            "recipient_address": wallet_founder3['address'],
            "amount": 10
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder3,
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


    #RUN
    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    # assert member 1 balance
    response_token_dao = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": dao_token_name,
        "wallet_address": wallet_founder1['address']
    })
    assert response_token_dao.status_code == 200
    balance_token_ot = response_token_dao.json()['balance']
    assert balance_token_ot == 10    

    # # #assert member 2 balance
    response_token_dao = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": dao_token_name,
        "wallet_address": wallet_founder2['address']
    })
    assert response_token_dao.status_code == 200
    balance_token_ot = response_token_dao.json()['balance']
    assert balance_token_ot == 10

    # # assert member 3 balance
    response_token_dao = requests.get(NODE_URL+'/get-balances', params={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": dao_token_name,
        "wallet_address": wallet_founder3['address']
    })
    assert response_token_dao.status_code == 200
    balance_token_ot = response_token_dao.json()['balance']
    assert balance_token_ot == 10

def test_lock_tokens(request):
    dao_details = request.config.cache.get('dao_details', None)
    wallet_founder1 = dao_details["wallet_founder1"]
    wallet_founder1_pid = dao_details["wallet_founder1_pid"]
    wallet_founder2 = dao_details["wallet_founder2"]
    wallet_founder2_pid = dao_details["wallet_founder2_pid"]
    wallet_founder3 = dao_details["wallet_founder3"]
    wallet_founder3_pid = dao_details["wallet_founder3_pid"]

    dao_token_name = dao_details["dao_token_name"]
    token_dao_address = request.config.cache.get('token_dao_address', None)

    #member 1 lock
    req = {
        "sc_address": token_dao_address,
        "function_called": "lock_tokens",
        "signers": [
            wallet_founder1['address']
        ],
        "params": {
            "value": [
                {
                    "token_code": dao_token_name,
                    "amount": 10
                }],
            "amount": 10,
            "person_id": wallet_founder1_pid
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder1,
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

    # member 2 lock
    req = {
        "sc_address": token_dao_address,
        "function_called": "lock_tokens",
        "signers": [
            wallet_founder2['address']
        ],
        "params": {
            "value": [
                {
                    "token_code": dao_token_name,
                    "amount": 10
                }],
            "amount": 10,
            "person_id": wallet_founder2_pid
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder2,
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

    # member 3 lock
    req = {
        "sc_address": token_dao_address,
        "function_called": "lock_tokens",
        "signers": [
            wallet_founder3['address']
        ],
        "params": {
            "value": [
                {
                    "token_code": dao_token_name,
                    "amount": 10
                }],
            "amount": 10,
            "person_id": wallet_founder3_pid
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder3,
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

    #assert mem 1 locked tokens
    params = {
            'table_name' : "dao_token_lock",
            'contract_address': token_dao_address,
            'unique_column': "person_id",
            'unique_value': wallet_founder1_pid
        }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"]
    assert response_val['data'][5]==10

    #assert mem 2 locked tokens
    params = {
        'table_name': "dao_token_lock",
        'contract_address': token_dao_address,
        'unique_column': "person_id",
        'unique_value': wallet_founder2_pid
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"]
    assert response_val['data'][5] == 10

    #assert mem 3 locked tokens
    params = {
        'table_name': "dao_token_lock",
        'contract_address': token_dao_address,
        'unique_column': "person_id",
        'unique_value': wallet_founder2_pid
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"]
    assert response_val['data'][5] == 10

def test_proposal_invest(request):
    dao_details = request.config.cache.get('dao_details', None)
    company_token_name = dao_details["company_token_name"]
    token_dao_address = request.config.cache.get('token_dao_address', None)
    wallet_company_founder = dao_details["wallet_company_founder"]

    req = {
        "sc_address": token_dao_address,
        "function_called": "create_proposal",
        "signers": [
            wallet_company_founder['address']
        ],
        "params": {

            "function_called": "invest",
            "params": {
                "value": [
                    {
                        "token_code": company_token_name,
                        "amount": 200
                    }],
                "wallet_to_invest": wallet_company_founder['address'],
                "invest_token_code": "NWRL",
                "invest_token_amount": 10,
                "token_to_recieve": company_token_name,
                "token_recieve_amt": 200
            },
            "block_index_reference": 234543,
            "voting_start_ts": 123324324,
            "voting_end_ts": 123325324
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_company_founder,
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

    params = {
            'table_name': "proposal_data",
            'contract_address': token_dao_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"]
    proposal_length_new = len(response_val["data"])
    assert proposal_length_new == 1
    proposal_id_resp = response_val["data"][0][1]
    request.config.cache.set('proposal_id_invest', proposal_id_resp)


def test_vote_on_proposal_invest(request):
    dao_details = request.config.cache.get('dao_details', None)
    wallet_founder1 = dao_details["wallet_founder1"]
    wallet_founder2 = dao_details["wallet_founder2"]
    token_dao_address = request.config.cache.get('token_dao_address', None)
    proposal_id = request.config.cache.get('proposal_id_invest', None)
    #vote 1
    req = {
        "sc_address": token_dao_address,
        "function_called": "vote_on_proposal",
        "signers": [
            wallet_founder1['address']
        ],
        "params": {
            "proposal_id": proposal_id,
            "vote": 1
        }
    }
    response = requests.post(NODE_URL+"/call-sc", json= req
    )
    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder1,
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
    
    params = {
        'table_name': "proposal_data",
        'contract_address': token_dao_address,
        'unique_column': "proposal_id",
        'unique_value': proposal_id
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val is not None
    current_yes_votes = response_val["data"][5]
    assert current_yes_votes == 10
    
    #vote 2
    req = {
        "sc_address": token_dao_address,
        "function_called": "vote_on_proposal",
        "signers": [
            wallet_founder2['address']
        ],
        "params": {
            "proposal_id": proposal_id,
            "vote": 1
        }
    }
    response = requests.post(NODE_URL+"/call-sc", json=req
                             )
    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder2,
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

    params = {
        'table_name': "proposal_data",
        'contract_address': token_dao_address,
        'unique_column': "proposal_id",
        'unique_value': proposal_id
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val is not None
    current_yes_votes = response_val["data"][5]
    assert current_yes_votes == 20

    #assert proposal status
    params = {
        'table_name': "proposal_data",
        'contract_address': token_dao_address,
        'unique_column': "proposal_id",
        'unique_value': proposal_id
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val is not None
    current_status = response_val["data"][9]
    assert current_status == 'accepted'


def test_proposal_disburse(request):
    dao_details = request.config.cache.get('dao_details', None)
    company_token_name = dao_details["company_token_name"]
    token_dao_address = request.config.cache.get('token_dao_address', None)
    wallet_company_founder = dao_details["wallet_company_founder"]

    req = {
        "sc_address": token_dao_address,
        "function_called": "disburse",
        "signers": [
            wallet_company_founder['address']
        ],

        "params": {
            "value": [
                {
                    "token_code": company_token_name,
                    "amount": 200
                }],
            "proposal_id":request.config.cache.get('proposal_id_invest', None),
            "block_index_reference": 234543,
            "voting_start_ts": 123324324,
            "voting_end_ts": 623325324
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL + '/call-sc', headers=headers, json=req
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": wallet_company_founder,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1
    response = requests.post(
        NODE_URL + '/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    params = {
        'table_name': "proposal_data",
        'contract_address': token_dao_address,
    }
    response = requests.get(NODE_URL + "/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"]
    proposal_length_new = len(response_val["data"])
    assert proposal_length_new == 1
    assert response_val["data"][0][9]=="disbursed"

# def test_proposal_payout(request):
#     dao_details = request.config.cache.get('dao_details', None)
#     wallet_founder1 = dao_details["wallet_founder1"]
#     company_token_name = dao_details["company_token_name"]
#     token_dao_address = request.config.cache.get('token_dao_address', None)
#     req = {
#         "sc_address": token_dao_address,
#         "function_called": "create_proposal",
#         "signers": [
#             wallet_founder1['address']
#         ],
#         "params": {
#             "function_called": "payout",
#             "params": {
#                 "asset_code": company_token_name,
#                 "asset_amount": "10"
#             },
#             "block_index_reference": 234543,
#             "voting_start_ts": 123324324,
#             "voting_end_ts": 123325324
#         }
#     }

#     headers = {
#         'Content-Type': 'application/json'
#     }

#     response = requests.post(NODE_URL+'/call-sc', headers=headers, json=req
#                              )

#     assert response.status_code == 200
#     unsigned_transaction = response.json()
#     assert unsigned_transaction['transaction']
#     assert len(unsigned_transaction['signatures']) == 0
#     unsigned_transaction['transaction']['fee'] = 1000000

#     response = requests.post(NODE_URL+'/sign-transaction', json={
#         "wallet_data": wallet_founder1,
#         "transaction_data": unsigned_transaction
#     })

#     assert response.status_code == 200
#     signed_transaction = response.json()
#     assert signed_transaction['transaction']
#     assert signed_transaction['signatures']
#     assert len(signed_transaction['signatures']) == 1
#     response = requests.post(
#         NODE_URL+'/validate-transaction', json=signed_transaction)
#     assert response.status_code == 200

#     if TEST_ENV == 'local':
#         response = requests.post(
#             NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
#     else:
#         print('Waiting to mine block')
#         time.sleep(BLOCK_WAIT_TIME)

#     params = {
#         'table_name': "proposal_data",
#         'contract_address': token_dao_address,
#     }
#     response = requests.get(NODE_URL+"/sc-states", params=params)
#     assert response.status_code == 200
#     response_val = response.json()
#     assert response_val["data"]
#     proposal_length_new = len(response_val["data"])
#     assert proposal_length_new == 2
#     proposal_id_resp = response_val["data"][1][1]
#     request.config.cache.set('proposal_id_payout', proposal_id_resp)


#   def test_vote_on_proposal_payout(request):

#     dao_details = request.config.cache.get('dao_details', None)
#     wallet_founder1 = dao_details["wallet_founder1"]
#     wallet_founder2 = dao_details["wallet_founder2"]

#     company_token_name = dao_details["company_token_name"]
#     token_dao_address = request.config.cache.get('token_dao_address', None)
#     proposal_id = request.config.cache.get('proposal_id_payout', None)

#     #vote 1
#     req = {
#         "sc_address": token_dao_address,
#         "function_called": "vote_on_proposal",
#         "signers": [
#             wallet_founder1['address']
#         ],
#         "params": {
#             "proposal_id": proposal_id,
#             "vote": 1
#         }
#     }
#     response = requests.post(NODE_URL+"/call-sc", json=req
#                              )
#     assert response.status_code == 200
#     unsigned_transaction = response.json()
#     assert unsigned_transaction['transaction']
#     assert len(unsigned_transaction['signatures']) == 0
#     unsigned_transaction['transaction']['fee'] = 1000000

#     response = requests.post(NODE_URL+'/sign-transaction', json={
#         "wallet_data": wallet_founder1,
#         "transaction_data": unsigned_transaction
#     })

#     assert response.status_code == 200
#     signed_transaction = response.json()
#     assert signed_transaction['transaction']
#     assert signed_transaction['signatures']
#     assert len(signed_transaction['signatures']) == 1

#     response = requests.post(
#         NODE_URL+'/validate-transaction', json=signed_transaction)
#     assert response.status_code == 200

#     if TEST_ENV == 'local':
#         response = requests.post(
#             NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
#     else:
#         print('Waiting to mine block')
#         time.sleep(BLOCK_WAIT_TIME)

#     params = {
#         'table_name': "proposal_data",
#         'contract_address': token_dao_address,
#         'unique_column': "proposal_id",
#         'unique_value': proposal_id
#     }
#     response = requests.get(NODE_URL+"/sc-state", params=params)
#     assert response.status_code == 200
#     response_val = response.json()
#     assert response_val is not None
#     current_yes_votes = response_val["data"][5]
#     assert current_yes_votes == 10

#     #vote 2
#     req = {
#         "sc_address": token_dao_address,
#         "function_called": "vote_on_proposal",
#         "signers": [
#             wallet_founder2['address']
#         ],
#         "params": {
#             "proposal_id": proposal_id,
#             "vote": 1
#         }
#     }
#     response = requests.post(NODE_URL+"/call-sc", json=req
#                              )
#     assert response.status_code == 200
#     unsigned_transaction = response.json()
#     assert unsigned_transaction['transaction']
#     assert len(unsigned_transaction['signatures']) == 0
#     unsigned_transaction['transaction']['fee'] = 1000000

#     response = requests.post(NODE_URL+'/sign-transaction', json={
#         "wallet_data": wallet_founder2,
#         "transaction_data": unsigned_transaction
#     })

#     assert response.status_code == 200
#     signed_transaction = response.json()
#     assert signed_transaction['transaction']
#     assert signed_transaction['signatures']
#     assert len(signed_transaction['signatures']) == 1

#     response = requests.post(
#         NODE_URL+'/validate-transaction', json=signed_transaction)
#     assert response.status_code == 200

#     if TEST_ENV == 'local':
#         response = requests.post(
#             NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
#     else:
#         print('Waiting to mine block')
#         time.sleep(BLOCK_WAIT_TIME)

#     params = {
#         'table_name': "proposal_data",
#         'contract_address': token_dao_address,
#         'unique_column': "proposal_id",
#         'unique_value': proposal_id
#     }
#     response = requests.get(NODE_URL+"/sc-state", params=params)
#     assert response.status_code == 200
#     response_val = response.json()
#     assert response_val is not None
#     current_yes_votes = response_val["data"][5]
#     assert current_yes_votes == 20

#     #assert proposal status
#     params = {
#         'table_name': "proposal_data",
#         'contract_address': token_dao_address,
#         'unique_column': "proposal_id",
#         'unique_value': proposal_id
#     }
#     response = requests.get(NODE_URL+"/sc-state", params=params)
#     assert response.status_code == 200
#     response_val = response.json()
#     assert response_val is not None
#     current_status = response_val["data"][9]
#     assert current_status == 'accepted'
    
#     response_token1 = requests.get(NODE_URL+'/get-balances', params={
#         "balance_type": "TOKEN_IN_WALLET",
#         "token_code": company_token_name,
#         "wallet_address": wallet_founder1['address']
#     })
#     assert response_token1.status_code == 200
#     balance_token1_resp = response_token1.json()
#     balance_token1 = balance_token1_resp['balance']
#     assert balance_token1 == 3