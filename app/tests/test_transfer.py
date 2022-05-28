from audioop import add
from random import random
import token
from fastapi.testclient import TestClient

from ..codes import updater
from ..migrations.init import init_newrl
import random

from ..main import app
from ..codes.contracts.nusd1 import nusd1

client = TestClient(app)

init_newrl()

_custodian_wallet = {"public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==","private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=","address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}

def create_wallet():
    response = client.get("/generate-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    assert wallet['address']
    assert wallet['public']
    assert wallet['private']

    response = client.post('/add-wallet', json={
        "custodian_address": _custodian_wallet['address'],
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

    custodian_wallet = {
        "address": _custodian_wallet['address'],
        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",
        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="
    }

    response = client.post('/sign-transaction', json={
        "wallet_data": _custodian_wallet,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    updater.mine(True)

    response = client.get('/download-state')
    assert response.status_code == 200
    state = response.json()

    wallets = state['wallets']
    wallet_in_state = next(
        x for x in wallets if x['wallet_address'] == wallet['address'])
    assert wallet_in_state
    return wallet


def create_token(wallet, custodian_wallet):
    response = client.post('/add-token', json={
        "token_name": "TestTOKEN",
        "token_code" : "",
        "token_type": "string",
        "first_owner": wallet['address'],
        "custodian": custodian_wallet['address'],
        "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
        "amount_created": 8888,
        "tokendecimal": 0,
        "disallowed_regions": [],
        "is_smart_contract_token": False,
        "token_attributes": {}
    })

    postedval = {"token_name": "TestTOKEN",
        "tokencode" : "",
        "token_type": "string",
        "first_owner": wallet['address'],
        "custodian": custodian_wallet['address'],
        "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
        "amount_created": 8888,
        "tokendecimal": 0,
        "disallowed_regions": [],
        "is_smart_contract_token": False,
        "token_attributes": {}}
    print(postedval)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = client.post('/sign-transaction', json={
        "wallet_data": custodian_wallet,
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
    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    print("running updater")
    updater.mine(True)

    response = client.get('/download-state')
    assert response.status_code == 200
    state = response.json()

    tokens = state['tokens']
    token_in_state = next(
        x for x in tokens if x['parent_transaction_code'] == signed_transaction['transaction']['trans_code'])
    assert token_in_state
    print("token exists in state")

    balances = state['balances']
    balance = next(x for x in balances if x['wallet_address'] ==
                   wallet['address'] and x['tokencode'] == token_in_state['tokencode'])
    assert balance
    print("token exists in balances")
    assert balance['balance'] == 8888
    print("token balance correct, returning tokencode")

    return token_in_state['tokencode']


def create_transfer(wallet1, wallet2, token1, token2):
    response = client.post('/add-transfer', json={
        "transfer_type": 4,
        "asset1_code": token1,
        "asset2_code": token2,
        "wallet1_address": wallet1['address'],
        "wallet2_address": wallet2['address'],
        "asset1_qty": 1000,
        "asset2_qty": 2000
    })

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = client.post('/sign-transaction', json={
        "wallet_data": wallet1,
        "transaction_data": unsigned_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/sign-transaction', json={
        "wallet_data": wallet2,
        "transaction_data": signed_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 2

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    updater.mine(True)


    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token1,
        "wallet_address": wallet1['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 7888

    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token2,
        "wallet_address": wallet1['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 2000

    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token1,
        "wallet_address": wallet2['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 1000

    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token2,
        "wallet_address": wallet2['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 6888


def test_transfer():
    custodian_wallet = _custodian_wallet

    wallet1 = create_wallet()
    wallet2 = create_wallet()
    print("created wallets with addresses, ",wallet1['address']," and ",wallet2['address'])

    token1 = create_token(wallet1, custodian_wallet)
    token2 = create_token(wallet2, custodian_wallet)
    print("tokens created")

    create_transfer(wallet1, wallet2, token1, token2)
    print("transfer done")

    response = client.get(f'/get-balances?balance_type=TOKEN_IN_WALLET&token_code={token1}&wallet_address={wallet1}')
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 8888


