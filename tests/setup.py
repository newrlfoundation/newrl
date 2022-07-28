import random
import string

NODE_URL = 'http://testnet.newrl.net:8182'
WALLET =  {'public': 'MKGFOKkyE2gLU7xzlhxZEl6+Ar+zXIQPEEkyCKeZbrlPoNzfP5/ugpx7HWsDEW3qsQ0cVTQ8+Sh2rPOV9f2Zcg==', 'private': 'x8zx8ZU+EYgLboxB2sw8i/ED91jjYkDKhLs0Ezu2c5E=', 'address': '0xa21c018881619441e23e4fe7f45405391bcd2cc6'}
BLOCK_WAIT_TIME = 35

def generate_random_token_code():
    return 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))