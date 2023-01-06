import json
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV
from test_add_wallet import add_wallet
from test_transfer import transfer_unilateral

STAKE_CT_ADDRESS = 'ct1111111111111111111111111111111111111115'


def test_stake():
    w1 = add_wallet()
    wallet_to_stake = w1['address']
    transfer_unilateral(WALLET, w1, 'NWRL', 1235)

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
        "sc_address": STAKE_CT_ADDRESS,
        "function_called": "stake_tokens",
        "signers": [
            WALLET['address']
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
    unsigned_transaction['transaction']['fee'] = 1000000

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