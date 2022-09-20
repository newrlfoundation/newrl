import random
import string
import os

WALLET = {"public": "09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee", "private": "d63e7ca37bcd6b43a6bdf281b2f9b4de7e64f027c0f741ffe12a105bf3955ec7", "address": "0x667663f36ac08e78bbf259f1361f02dc7dad593b"}
BLOCK_WAIT_TIME = 15


def generate_random_token_code():
    return 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

TEST_ENV = os.environ.get('TEST_ENV')

if TEST_ENV == 'local':
    NODE_URL = 'http://localhost:4018'
else:
    NODE_URL = 'http://devnet.newrl.net:8420'
