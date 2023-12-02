import random
import string
import os

WALLET = CUSTODIAN_WALLET = { "public": "51017a461ecccdc082a49c3f6e17bb9a6259990f6c4d1c1dbb4e067878ddfa71cb4afbe6134bad588395edde20b92c6dd5abab4108d7e6aeb42a06229205cabb", "private": "92a365e63db963a76c0aa1389aee1ae4d25a4539311595820b295d3a77e07618", "address": "0x1342e0ae1664734cbbe522030c7399d6003a07a8"}
# WALLET = {"public": "1efe5519bc0f207bb295e897160e41648c0150366b0202003ef9fdf0be3e1ac5afd185c8843ac3bf1ea4c0c8592c931e34fa6c7744ed34ab6726d6db33799e69", "private": "dc2fc8d7cd6a780c4cc6f5eca2784e183e3dc69d5fe5e08fe5bd088103aba5d6", "address": "0xf84a44f998227c0e70f21509a22b879a9d7cbb3d"}
BLOCK_WAIT_TIME = 15
MIN_NEWRL_FEE = 1000000
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def generate_random_token_code():
    return 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

TEST_ENV = os.environ.get('TEST_ENV')

if TEST_ENV == 'local':
    NODE_URL = 'http://localhost:4018'
else:
    # NODE_URL = 'https://devnetapi.newrl.net'
    # NODE_URL = 'https://devnetapi.newrl.net'
    NODE_URL = 'http://65.0.104.146:8424'
