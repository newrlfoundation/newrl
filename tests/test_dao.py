import logging
import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV

dao_manager_address = "ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7"
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

    response = requests.get(NODE_URL+'/download-state')
    assert response.status_code == 200
    state = response.json()

    wallets = state['wallets']
    wallet_in_state = next(
        x for x in wallets if x['wallet_address'] == wallet['address'])
    assert wallet_in_state

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


wallet_founder1 = create_wallet()
wallet_founder2 = create_wallet()
wallet_founder3 = create_wallet()
wallet_member1 = create_wallet()
member_pid = get_pid(wallet_member1)

wallet_dao = create_wallet()
dao_token_name = "dao_token".join(random.choices(string.ascii_uppercase + string.digits, k=10))

def test_create_mem_dao():
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
            "dao_name": "membership_dao_ver1",
            "dao_address": ct_address,
            "founders": [
                wallet_founder1['address'],
                wallet_founder2['address'],
                wallet_founder3['address']
            ],
            "dao_main_sc": "membership_dao_ver1",
            "dao_main_sc_version": "1.0.0",
            "contractspecs": {
                "token_name": dao_token_name,
                "dao_wallet_address": wallet_dao["address"],
                "max_members": 999999999,
                "max_voting_time": 300000,
                "total_votes": 3,
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
                    "payout": [
                        -1
                    ],
                    "lock_tokens": None,
                    "issue_token": None,
                    "initialize_membership": None
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
    return ct_address

mem_dao_address = test_create_mem_dao()
proposal_id = ""

def test_initialize_dao():
    
    req_json = {
        "sc_address": mem_dao_address,
        "function_called": "initialize_membership",
        "signers": [
            wallet_founder1['address']
        ],
        "params": {}

    }
    response = requests.post(NODE_URL+'/call-sc', json=req_json
    )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

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

    founder_pids = []
    response = requests.get(
        NODE_URL+"/get-wallet", params={'wallet_address': wallet_founder1["address"]})
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["person_id"]
    founder_pids.append(response_val["person_id"])

    response = requests.get(
        NODE_URL+"/get-wallet", params={'wallet_address': wallet_founder2["address"]})
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["person_id"]
    founder_pids.append(response_val["person_id"])

    response = requests.get(
        NODE_URL+"/get-wallet", params={'wallet_address': wallet_founder3["address"]})
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["person_id"]
    founder_pids.append(response_val["person_id"])

    for founder in founder_pids:
        params = {
            'table_name' : "dao_membership",
            'contract_address': mem_dao_address,
            'unique_column': "member_person_id",
            'unique_value': founder
        }
        response = requests.get(NODE_URL+"/sc-state", params=params)
        assert response.status_code == 200
        response_val = response.json()
        assert response_val["data"]


def test_proposal_add_member():

    #get member pid
    global member_pid

    req = {
        "sc_address": mem_dao_address,
        "function_called": "create_proposal",
        "signers": [
            wallet_founder1['address']
        ],
        "params": {
            "function_called": "add_member",
            "params":
            {
                "member_person_id": member_pid
            },
            "block_index_reference": 234543,
            "voting_start_ts": 123324324,
            "voting_end_ts": 123325324,
        }
    }

    response = requests.post(NODE_URL+"/call-sc", json= req
    )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": wallet_founder1,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    #TODO refactor get proposal id logic (proposal id is auto gen now)
    #getdao pid

    params = {
        'table_name': "proposal_data",
        'contract_address': mem_dao_address,
    }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"] is not None
    proposal_length = len(response_val["data"])

    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    if TEST_ENV == 'local':
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    global proposal_id
    #TODO asset new state creation instead of len
    params = {
            'table_name': "proposal_data",
            'contract_address': mem_dao_address,
        }
    response = requests.get(NODE_URL+"/sc-states", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val["data"]
    proposal_length_new = len(response_val["data"])
    assert proposal_length_new == proposal_length+1
    proposal_id_resp =  response_val["data"][0][1]
    proposal_id = proposal_id_resp


def test_vote_proposal_add_memeber():
    global proposal_id
    #vote 1
    req = {
        "sc_address": mem_dao_address,
        "function_called": "vote_on_proposal",
        "signers": [
            wallet_founder2['address']
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
        'contract_address': mem_dao_address,
        'unique_column': "proposal_id",
        'unique_value': proposal_id
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val is not None
    current_yes_votes = response_val["data"][5]
    assert current_yes_votes == 1

    #vote 2
    req = {
        "sc_address": mem_dao_address,
        "function_called": "vote_on_proposal",
        "signers": [
            wallet_founder3['address']
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

    params = {
        'table_name': "proposal_data",
        'contract_address': mem_dao_address,
        'unique_column': "proposal_id",
        'unique_value': proposal_id
    }
    response = requests.get(NODE_URL+"/sc-state", params=params)
    assert response.status_code == 200
    response_val = response.json()
    assert response_val is not None
    current_yes_votes = response_val["data"][5]
    assert current_yes_votes == 2

    