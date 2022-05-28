import time
import sqlite3

from app.codes import updater
from ..codes.db_updater import update_wallet_token_balance
from fastapi.testclient import TestClient
from ..ntypes import NUSD_TOKEN_CODE
from ..constants import NEWRL_DB
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def check_newrl_wallet_balance(wallet_address, _balance, token='NWRL'):
    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token,
        "wallet_address": wallet_address
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == _balance


def test_mining_reward():
    response = client.get("/get-node-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    wallet_address = wallet['wallet_address']
    assert wallet_address

    check_newrl_wallet_balance(wallet_address, 1500001000.0)

    updater.mine(True)
    assert response.status_code == 200
    check_newrl_wallet_balance(wallet_address, 1500002000.0)
    
    time.sleep(2)
    updater.mine(True)
    assert response.status_code == 200
    check_newrl_wallet_balance(wallet_address, 1500002000.0)
    
    time.sleep(5)
    updater.mine(True)
    assert response.status_code == 200
    check_newrl_wallet_balance(wallet_address, 1500002000.0)


def test_transaction_fee_payment():
    check_newrl_wallet_balance(TREASURY_WALLET_ADDRESS, None, NUSD_TOKEN_CODE)
    # create_wallet_with_fee(2)
    # check_newrl_wallet_balance(TREASURY_WALLET_ADDRESS, None, NUSD_TOKEN_CODE)

    set_balance('0xc29193dbab0fe018d878e258c93064f01210ec1a', NUSD_TOKEN_CODE, 5)
    create_wallet_with_fee(2)
    check_newrl_wallet_balance(TREASURY_WALLET_ADDRESS, 2, NUSD_TOKEN_CODE)


def create_wallet_with_fee(fee):
    response = client.get("/generate-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    assert wallet['address']
    assert wallet['public']
    assert wallet['private']

    response = client.post('/add-wallet', json={
        "custodian_address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
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

    unsigned_transaction['transaction']['fee'] = fee
    unsigned_transaction['transaction']['currency'] = NUSD_TOKEN_CODE

    custodian_wallet = {
        "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",
        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="
    }

    response = client.post('/sign-transaction', json={
        "wallet_data": custodian_wallet,
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
    assert response.status_code == 200


def set_balance(wallet, token, balance):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    update_wallet_token_balance(cur, wallet, token, balance)
    con.commit()
    con.close()
