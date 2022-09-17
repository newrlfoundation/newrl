import random
import string
import os

WALLET = {"public": "CcGRdIzGC0ODmycwg8xWWBHCb1zlSxftS0oXxh561riA/HrDCBucDPKHVuohzlAXibWej5ED82aMzyyGEIYo7g==", "private": "1j58o3vNa0OmvfKBsvm03n5k8CfA90H/4SoQW/OVXsc=", "address": "0x667663f36ac08e78bbf259f1361f02dc7dad593b"}
BLOCK_WAIT_TIME = 15

def generate_random_token_code():
    return 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

TEST_ENV = os.environ.get('TEST_ENV')

if TEST_ENV == 'local':
    NODE_URL = 'http://localhost:4018'
else:
    NODE_URL = 'http://testnet.newrl.net:8182'
