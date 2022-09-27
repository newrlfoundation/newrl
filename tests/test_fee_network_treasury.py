import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV
from tests.utils import create_wallet, get_balance


def test_fee():
    #get current trasury balance
    #invoke a type 5 with fee 1
    #confirm if treasury contract is having fee add up as balance + existing balance
    
    network_treasury_address ="ctb020e608d11c235724e676d021a08f8da6c64eb8"
    init_treasury_contract_balance = get_balance(network_treasury_address,"NWRL")

    fee = 5

    wallet1 = create_wallet()

    req_json = {
        "transfer_type": 5,
        "asset1_code": "NWRL",
        "asset2_code": "",
        "wallet1_address": WALLET['address'],
        "wallet2_address": wallet1['address'],
        "asset1_qty": 10,
        "description": "",
        "additional_data": {}
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(NODE_URL+'/add-transfer', headers=headers, json=req_json
                             )

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    unsigned_transaction['fee'] = fee

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

    post_treasury_contract_balance = get_balance("", "NWRL")

    assert post_treasury_contract_balance == init_treasury_contract_balance + fee



