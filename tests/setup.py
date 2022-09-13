import random
import string
import os

WALLET = WALLET = {"public": "9ed7d27889d0d17c9f729afc806684cadf32d131ca1078bcd42d7ca954c9317cef739f647c5119ca4f74fc24fb027bfac9b38b0ee5bb5025ecbb82a8e7cb95d1",
                   "private": "e31b507aecd43490e61a3228dc36227a33ee5aac6c608a390e53202ca8084720",
                   "address": "0xe738ffa75c377d07819d21170c7594aa89ce1618"}
BLOCK_WAIT_TIME = 45

def generate_random_token_code():
    return 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

TEST_ENV = os.environ.get('TEST_ENV')

if TEST_ENV == 'local':
    NODE_URL = 'http://localhost:4018'
else:
    NODE_URL = 'http://testnet.newrl.net:8182'
