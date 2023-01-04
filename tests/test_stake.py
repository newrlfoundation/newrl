import json
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME, TEST_ENV

STAKE_CT_ADDRESS = 'ctcdb91798f3022dee388b7ad55eeea527f98caee4'


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
        response = requests.post(
            NODE_URL + '/run-updater?add_to_chain_before_consensus=true')
    else:
        print('Waiting to mine block')
        time.sleep(BLOCK_WAIT_TIME)

    response = requests.get(NODE_URL+'/download-state')
    assert response.status_code == 200
    state = response.json()

    wallets = state['wallets']
    wallet_in_state = next(
        x for x in wallets if x['wallet_address'] == wallet['address'])
    assert wallet_in_state

    print("Wallet created with address "+wallet['address'])
    print('Test passed.')
    return wallet


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