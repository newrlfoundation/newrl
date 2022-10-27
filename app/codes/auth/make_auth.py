import os.path
import hashlib
import json
import argparse

from ...constants import AUTH_FILE_PATH
from ..kycwallet import generate_wallet_address
from ..utils import get_person_id_for_wallet_address


def make_auth_json(createnewwallet = False):
    if os.path.isfile(AUTH_FILE_PATH):
        print('Auth file exists already. Not creating one.')
        return
    if not createnewwallet:
        # wallet_exists = input('Do you have an existing wallet?[Y/n]:')
        # if wallet_exists == 'Y' or wallet_exists == 'y'):
        auth_data = json.loads(input('Paste your .auth.json file contents:\n'))
        wallet = auth_data
        with open(AUTH_FILE_PATH, 'w') as f:
            json.dump(auth_data, f)
    else:
        wallet = generate_wallet_address()

        auth_data = wallet

        with open(AUTH_FILE_PATH, 'w') as f:
            json.dump(auth_data, f)
    
    print('Share the public key with a custodian to create your wallet on chain')
    print('Public key: ', wallet['public'])
    return wallet['public']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--createnewwallet", help="run the node local only with no network connection", action="store_true")
    args = parser.parse_args()
    
    make_auth_json(args.createnewwallet)