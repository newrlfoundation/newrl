import json
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV
from tests.test_mem_dao import create_wallet

STAKE_CT_ADDRESS = 'ctcdb91798f3022dee388b7ad55eeea527f98caee4'

def test_stake():
    wallet_to_stake = create_wallet()['address']

    amount_to_stake = 1234

    response = requests.get(NODE_URL + f'/sc-state?table_name=stake_ledger&contract_address={STAKE_CT_ADDRESS}&unique_column=wallet_address&unique_value={wallet_to_stake}')
    assert response.status_code == 200
    response = response.json()
    assert response['status'] == 'SUCCESS'
    if response['data'] is None:
        initial_stake = 0
    else:
        assert response['data'][2] == wallet_to_stake
        initial_stake = response['data'][3]
    
    stake_payload = {
        "sc_address": "ctcdb91798f3022dee388b7ad55eeea527f98caee4",
        "function_called": "stake_tokens",
        "signers": [
            "0x667663f36ac08e78bbf259f1361f02dc7dad593b"
        ],
        "params": {
            "value": [
                {
                    "token_code": "NWRL",
                    "amount": amount_to_stake
                }],
                "token_amount": amount_to_stake,
                "wallet_address": wallet_to_stake
            
        }
    }

    response = requests.post(NODE_URL + '/call-sc', json=stake_payload)

    unsigned_transaction = response.json()

    response = requests.post(NODE_URL + '/sign-transaction', json={
        "wallet_data": WALLET,
        "transaction_data": unsigned_transaction
    })

    signed_transaction = response.json()
    t = json.loads(json.dumps(signed_transaction))

    response = requests.post(NODE_URL + '/submit-transaction', json=signed_transaction
    , timeout=1)

    if TEST_ENV == 'local':
        response = requests.post(NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL + f'/sc-state?table_name=stake_ledger&contract_address={STAKE_CT_ADDRESS}&unique_column=wallet_address&unique_value={wallet_to_stake}')
    assert response.status_code == 200
    response = response.json()
    assert response['status'] == 'SUCCESS'
    assert response['data'][2] == wallet_to_stake
    new_stake = response['data'][3]

    assert new_stake == initial_stake + amount_to_stake

    print('Test passed.')


if __name__ == '__main__':
    test_stake()