import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME
from utils import sign_and_wait_mine
from test_add_wallet import add_wallet


def test_trustscore_update():
    source_wallet_address = WALLET['address']
    destination_wallet_address = add_wallet()['address']
    response = requests.get(NODE_URL + f'/get-trustscore-wallets?dst_wallet_address={destination_wallet_address}&src_wallet_address={source_wallet_address}')
    print(response.json())
    if response.status_code == 200:
        current_trust_score = response.json()['trust_score']
    else:
        current_trust_score = 0
    trust_score_update_request = {
        "source_address": source_wallet_address,
        "destination_address": destination_wallet_address,
        "tscore": current_trust_score + 1
    }

    response = requests.post(NODE_URL + '/update-trustscore', json=trust_score_update_request)
    unsigned_transaction = response.json()
    unsigned_transaction['transaction']['fee'] = 1000000

    sign_and_wait_mine(unsigned_transaction)
    
    response = requests.get(NODE_URL + f'/get-trustscore-wallets?dst_wallet_address={destination_wallet_address}&src_wallet_address={source_wallet_address}')
    new_trust_score = response.json()['trust_score']

    assert new_trust_score == current_trust_score + 1
    print('Test passed.')


if __name__ == '__main__':
    test_trustscore_update()