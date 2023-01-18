import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV
from setup import generate_random_token_code
from test_add_wallet import add_wallet
from test_add_token import add_token
from test_fee_payer import add_token as add_token_fee_payer


def test_transfer_unilateral():
    from_wallet = WALLET
    to_wallet = add_wallet()
    transfer_unilateral(WALLET, to_wallet, 'NWRL', 5000000)
    token = add_token(from_wallet['address'])
    transfer_unilateral(from_wallet, to_wallet, token['tokencode'], 100)

def test_transfer_nwrl():
    from_wallet = WALLET
    to_wallet = add_wallet()
    # token = add_token(from_wallet['address'])
    transfer_unilateral(from_wallet, to_wallet, 'NWRL', 100)
    

def transfer_unilateral(from_wallet, to_wallet, token_code, amount):
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
    
    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": from_wallet,
    "transaction_data": unsigned_transaction
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


def transfer_bilateral(wallet1, wallet2, token_code1, token_code2, amount1, amount2, skip_wallet2=False, fee_payer_wallet=None, skip_fee_payer_sign=True):
    # token_code = token['tokencode']
    req ={
        "transfer_type": 4,
        "asset1_code": token_code1,
        "asset2_code": token_code2,
        "wallet1_address": wallet1['address'],
        "wallet2_address": None if skip_wallet2 else wallet2['address'],
        "asset1_qty": amount1,
        "asset2_qty": amount2,
        "description": "",
        "additional_data": {}
    }
    response = requests.post(NODE_URL + '/add-transfer', json=req)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000
    if fee_payer_wallet is not None:
        unsigned_transaction['transaction']['fee_payer'] = fee_payer_wallet['address']
    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": wallet1,
    "transaction_data": unsigned_transaction
    })
    signed_transaction = response.json()
    response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": wallet2,
    "transaction_data": signed_transaction
    })
    signed_transaction = response.json()

    if fee_payer_wallet is not None and not skip_fee_payer_sign:
        response = requests.post(NODE_URL + '/sign-transaction', json={
            "wallet_data": fee_payer_wallet,
            "transaction_data": signed_transaction
        })
        signed_transaction = response.json()

    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)
    
    # response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token_code1}&wallet_address={wallet1['address']}")
    # assert response.status_code == 200
    # balance = response.json()['balance']
    # assert balance == amount1


    print('Test passed.')

def test_transfer_bilateral():
    wallet1 = add_wallet()
    wallet2 = add_wallet()
    transfer_unilateral(WALLET, wallet1, 'NWRL', 3000000)
    transfer_unilateral(WALLET, wallet2, 'NWRL', 3000000)
    token1 = add_token(wallet1['address'])
    token2 = add_token(wallet2['address'])

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 100
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == None
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 100
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == None

    transfer_bilateral(wallet1, wallet2, 
        token1['tokencode'], token2['tokencode'], 5, 10)
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 95

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 5
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 10

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 90

    print('Test passed.')


def test_transfer_bilateral_single_wallet_in_txn():
    wallet1 = add_wallet()
    wallet2 = add_wallet()
    transfer_unilateral(WALLET, wallet1, 'NWRL', 3000000)
    transfer_unilateral(WALLET, wallet2, 'NWRL', 3000000)
    token1 = add_token(wallet1['address'])
    token2 = add_token(wallet2['address'])

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 100
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == None
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 100
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == None

    transfer_bilateral(wallet1, wallet2, 
        token1['tokencode'], token2['tokencode'], 5, 10, skip_wallet2=True)
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 95

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 5
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 10

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 90

    print('Test passed.')


def test_transfer_bilateral_single_wallet_in_txn_fee_payer():
    wallet1 = add_wallet()
    wallet2 = add_wallet()
    transfer_unilateral(WALLET, wallet1, 'NWRL', 3000000)
    transfer_unilateral(WALLET, wallet2, 'NWRL', 3000000)
    token1 = add_token(wallet1['address'])
    token2 = add_token(wallet2['address'])

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 100

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == None

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 100

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == None

    transfer_bilateral(wallet1, wallet2,
                       token1['tokencode'], token2['tokencode'], 5, 10, skip_wallet2=True, fee_payer_wallet= WALLET, skip_fee_payer_sign= False)

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 95

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 5

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet1['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 10

    response = requests.get(
        NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token2['tokencode']}&wallet_address={wallet2['address']}")
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 90

    print('Test passed.')
