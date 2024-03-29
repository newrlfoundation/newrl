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

def test_create_sample_template(request):
    response_ct_add = requests.get(NODE_URL+"/generate-contract-address")
    assert response_ct_add.status_code == 200
    ct_address = response_ct_add.json()
    response = requests.post(NODE_URL+'/add-sc', json={
        "sc_address": ct_address,
        "sc_name": "sample_template",
        "version": "1.0.0",
        "creator": WALLET['address'],
        "actmode": "hybrid",
        "signatories": {"initialise_liquidity": None, "value_issue": None, "update_entry": None, "create_entry": None, "sample_validate": None,"sample_validate_exp":None,"sample_validate_test":[WALLET['address']]},
        "contractspecs": {},
        "legalparams": {}
    })
    print(response.text)
    assert response.status_code == 200
    unsigned_transaction=response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response=requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction=response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response=requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200
    assert response.json()['response']['valid']
    if TEST_ENV == 'local':
        response=requests.post(
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
    request.config.cache.set('st_address', ct_address) 

    
def test_sign_and_submit_with_non_sig_wallet(request):
    wallet1 = create_wallet()
    st_address = request.config.cache.get('st_address', None)
    request.config.cache.set('wallet1', wallet1)
    req_json = {
        "sc_address": st_address,
        "function_called": "sample_validate_test",
        "signers": [
            wallet1['address']
        ],
        "params": {
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
    
    assert response.json()["response"]["valid"] == False

    
def test_sign_and_submit_all_wallets(request):
    wallet1 = create_wallet()
    st_address = request.config.cache.get('st_address', None)
    request.config.cache.set('wallet1', wallet1)
    req_json = {
        "sc_address": st_address,
        "function_called": "sample_validate_test",
        "signers": [
            wallet1['address'],
            WALLET['address']
        ],
        "params": {
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

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": signed_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 2

    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    
    assert response.json()["response"]["valid"] == True


def test_sign_and_submit_none_sigs(request):
    wallet1 = create_wallet()
    st_address = request.config.cache.get('st_address', None)
    request.config.cache.set('wallet1', wallet1)
    req_json = {
        "sc_address": st_address,
        "function_called": "sample_validate",
        "signers": [
            WALLET['address']
        ],
        "params": {
            "amount_to_issue": 1,
            "address_to_issue": WALLET['address'],
            "value": [
                {
                    "token_code": "NWRL",
                    "amount": 1
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
    
    assert response.json()["response"]["valid"] == True

    

def test_sign_and_submit_for_method_with_multiple_sigs(request):
    #two signatories
    #one sign from signatories
    #one sign from non signatories

    #contract creation
    response_ct_add = requests.get(NODE_URL+"/generate-contract-address")
    assert response_ct_add.status_code == 200
    ct_address = response_ct_add.json()
    wallet0 = create_wallet()
    response = requests.post(NODE_URL+'/add-sc', json={
        "sc_address": ct_address,
        "sc_name": "sample_template",
        "version": "1.0.0",
        "creator": WALLET['address'],
        "actmode": "hybrid",
        "signatories": {"initialise_liquidity": None, "value_issue": None, "update_entry": None, "create_entry": None, "sample_validate": None,"sample_validate_exp":None,"sample_validate_test":[WALLET['address'],wallet0['address']]},
        "contractspecs": {},
        "legalparams": {}
    })
    print(response.text)
    assert response.status_code == 200
    unsigned_transaction=response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    unsigned_transaction['transaction']['fee'] = 1000000

    response=requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction=response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response=requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    assert response.status_code == 200
    assert response.json()['response']['valid']
    if TEST_ENV == 'local':
        response=requests.post(
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

    wallet1 = create_wallet()
    st_address = ct_address
    request.config.cache.set('wallet1', wallet1)
    req_json = {
        "sc_address": st_address,
        "function_called": "sample_validate_test",
        "signers": [
            wallet1['address'],
            WALLET['address']
        ],
        "params": {
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

    response = requests.post(NODE_URL+'/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": signed_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 2

    response = requests.post(
        NODE_URL+'/validate-transaction', json=signed_transaction)
    
    assert response.json()["response"]["valid"] == True
    