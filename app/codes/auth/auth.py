import logging
import sys
import json

from ...Configuration import Configuration
from ...constants import AUTH_FILE_PATH
from ..crypto import sign_object

logger = logging.getLogger(__name__)


def get_node_wallet_public():
    wallet = get_wallet()
    if wallet:
        return {
            'address': wallet['address'],
            'public': wallet['public']
        }
    else:
        return None


def get_node_wallet_address():
    wallet = get_wallet()
    if wallet:
        return wallet['address']
    else:
        return Configuration.config("ZERO_ADDRESS")


def get_wallet():
    with open(AUTH_FILE_PATH, 'r') as f:
        auth_data = json.load(f)
        wallet = auth_data
        if 'wallet' in wallet:
            return wallet['wallet']
        else:
            return wallet
        # if 'private' not in wallet:
        #     raise Exception('Invalid auth file')
        return wallet


def get_auth():
    try:
        with open(AUTH_FILE_PATH, 'r') as f:
            auth_data = json.load(f)
            wallet = auth_data
            private_key = wallet['private']
            auth_data = {
                'wallet_id': wallet['address'],
                'public': wallet['public'],
            }
            auth_data['signature'] = sign_object(private_key, auth_data)
            return auth_data
    except ValueError as e:        
        logger.error(e)
        auth_data = {}
        print(
            f'Could not use the wallet data. Please ensure correct format is present')
        exit()
    except Exception as e:
        logger.error(e)
        auth_data = {}
        print(f'Could not get auth data. Make auth file {AUTH_FILE_PATH} is present. Exiting.')
        print('Generate one by running installation')
        exit()
