import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV, MIN_NEWRL_FEE
from test_add_wallet import add_wallet
from test_add_token import add_token
from test_transfer import transfer_unilateral

def test_conflicting_transactions_in_block():
    from_wallet = add_wallet()
    to_wallet = add_wallet()
    amount = 110
    token = add_token(from_wallet['address'], amount)

    transfer_unilateral(WALLET, from_wallet, 'NWRL', 10 * MIN_NEWRL_FEE)

    token_code = token['tokencode']
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
    unsigned_transaction = response.json()    
    unsigned_transaction['transaction']['fee'] = MIN_NEWRL_FEE
    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": from_wallet,
        "transaction_data": unsigned_transaction
    })
    signed_transaction = response.json()
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    assert response.json()['response']['valid']

    req ={
        "transfer_type": 5,
        "asset1_code": token_code,
        "asset2_code": "",
        "wallet1_address": from_wallet['address'],
        "wallet2_address": to_wallet['address'],
        "asset1_qty": amount,
        "description": "t2",
        "additional_data": {}
    }
    response = requests.post(NODE_URL + '/add-transfer', json=req)
    unsigned_transaction = response.json()    
    unsigned_transaction['transaction']['fee'] = MIN_NEWRL_FEE
    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": from_wallet,
        "transaction_data": unsigned_transaction
    })
    signed_transaction = response.json()
    response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
    assert response.json()['response']['valid']

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token_code}&wallet_address={to_wallet['address']}")
    balance = response.json()['balance']
    assert balance == amount
    
    response = requests.get(NODE_URL + f"/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token_code}&wallet_address={from_wallet['address']}")
    balance = response.json()['balance']
    assert balance == 0