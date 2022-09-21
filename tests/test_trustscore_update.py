import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME
from utils import sign_and_wait_mine


def test_trustscore_update():
    source_wallet_address = WALLET['address']
    destination_wallet_address = '0x9fd9ffeff71a0bbbcdf9761445e156a447c9ac14'
    response = requests.get(NODE_URL + f'/get-trustscore-wallets?dst_wallet_address={destination_wallet_address}&src_wallet_address={source_wallet_address}')
    current_trust_score = response.json()['trust_score']
    trust_score_update_request = {
        "source_address": source_wallet_address,
        "destination_address": destination_wallet_address,
        "tscore": current_trust_score + 1
    }

    response = requests.post(NODE_URL + '/update-trustscore', json=trust_score_update_request)
    unsigned_transaction = response.json()
    sign_and_wait_mine(unsigned_transaction)
    
    response = requests.get(NODE_URL + f'/get-trustscore-wallets?dst_wallet_address={destination_wallet_address}&src_wallet_address={source_wallet_address}')
    new_trust_score = response.json()['trust_score']

    assert new_trust_score == current_trust_score + 1
    print('Test passed.')


if __name__ == '__main__':
    test_trustscore_update()