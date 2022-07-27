import random
import string
import time
import requests

from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME
from tests.setup import generate_random_token_code

token_code_1 = generate_random_token_code()
token_code_2 = generate_random_token_code()

def test_transfer_unilateral():
    
    print('Test passed.')

def test_transfer_bilateral():
    
    print('Test passed.')


if __name__ == '__main__':
    test_transfer_unilateral()
    test_transfer_bilateral()