import time
import sqlite3

from app.codes import updater
from app.codes.auth.auth import get_wallet
from ..Configuration import Configuration
from ..codes.db_updater import update_wallet_token_balance
from fastapi.testclient import TestClient
from ..ntypes import NUSD_TOKEN_CODE
from ..constants import NEWRL_DB, TIME_BETWEEN_BLOCKS_SECONDS
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def get_wallet_balance(wallet_address, token='NWRL'):
    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token,
        "wallet_address": wallet_address
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    return balance


def check_newrl_wallet_balance(wallet_address, _balance, token='NWRL'):
    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token,
        "wallet_address": wallet_address
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == _balance


def create_wallet_with_fee(fee, custodian_wallet=None):
    response = client.get("/generate-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    assert wallet['address']
    assert wallet['public']
    assert wallet['private']

    if custodian_wallet is None:
        custodian_wallet = get_wallet()

    response = client.post('/add-wallet', json={
        "custodian_address": custodian_wallet['address'],
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
    return wallet


def set_balance(wallet, token, balance):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    update_wallet_token_balance(cur, wallet, token, balance)
    con.commit()
    con.close()


def test_mining_reward():
    response = client.get("/get-node-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    wallet_address = wallet['wallet_address']
    assert wallet_address

    current_balance = get_wallet_balance(wallet_address=wallet_address)

    updater.mine(True)
    new_balance = get_wallet_balance(wallet_address=wallet_address)
    assert new_balance == current_balance + 1000


def test_transaction_fee_payment():
    response = client.get("/get-node-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    wallet_address = wallet['wallet_address']

    set_balance(wallet_address, NUSD_TOKEN_CODE, 100)
    set_balance(Configuration.config("TREASURY_WALLET_ADDRESS"), NUSD_TOKEN_CODE, 500)
    current_treasury_balance = get_wallet_balance(Configuration.config("TREASURY_WALLET_ADDRESS"), NUSD_TOKEN_CODE)
    wallet = create_wallet_with_fee(0)
    
    set_balance(wallet['address'], NUSD_TOKEN_CODE, 100)

    time.sleep(TIME_BETWEEN_BLOCKS_SECONDS + 1)
    
    create_wallet_with_fee(23, custodian_wallet=wallet)
    new_treasury_balance = get_wallet_balance(Configuration.config("TREASURY_WALLET_ADDRESS"), NUSD_TOKEN_CODE)
    assert new_treasury_balance == current_treasury_balance + 23
