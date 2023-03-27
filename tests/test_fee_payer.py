import time
import requests
import random
import string

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV

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


def test_fee_payer():
    w1 = add_wallet()
    tk1 = add_token(custodian_wallet=w1)
    check_token_present(tk1, should_fail=True)
    
    tk2 = add_token(custodian_wallet=w1, fee_payer_wallet=WALLET)
    check_token_present(tk2)
    
    tk2 = add_token(custodian_wallet=w1, fee_payer_wallet=WALLET, skip_custodian_sign=True)
    check_token_present(tk2, should_fail=True)

    tk2 = add_token(custodian_wallet=w1, fee_payer_wallet=WALLET, skip_fee_payer_sign=True)
    check_token_present(tk2, should_fail=True)
    
def test_fee_payer_type5():

    #create 2 wallets
    w1= add_wallet()
    w2= add_wallet()

    #create tokens and fund wallet 1
    tk1 = add_token(custodian_wallet=w1, wallet_to_credit = w1['address'],fee_payer_wallet=WALLET, amount = 500)
    check_token_present(tk1)

    #do a type 5 with WALLET as fee payer
    transfer_unilateral(w1,w2,tk1,200,WALLET)
    pass


def transfer_unilateral(from_wallet, to_wallet, token_code, amount, fee_payer_wallet = WALLET):
    # token_code = token['tokencode']
    req ={
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
    unsigned_transaction['transaction']['fee_payer'] = fee_payer_wallet['address']

    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": from_wallet,
    "transaction_data": unsigned_transaction
    })
    signed_transaction = response.json()

    #fee payer sign
    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET,
    "transaction_data": signed_transaction
    })
    signed_transaction = response.json()

    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token_code}&wallet_address={to_wallet['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == amount


    print('Test passed.')

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
