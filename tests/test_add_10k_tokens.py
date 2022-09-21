import random
import string
import time
import base64
import requests


from setup import NODE_URL, WALLET, BLOCK_WAIT_TIME

def sign_transaction(wallet_data, transaction_data):
    """Sign a transaction using a given wallet"""
    address = wallet_data['address']
    private_key_bytes = base64.b64decode(wallet_data['private'])
    public_key_bytes = base64.b64decode(wallet_data['public'])
    if not private_key_bytes:
        print("No private key found for the address")
        return False

    transaction_manager = Transactionmanager()
    transaction_manager.set_transaction_data(transaction_data)
    if not check_signing_address(transaction_manager.transaction, address):
        return False

    signtransbytes = transaction_manager.sign_transaction(private_key_bytes, address)
    print("signed msg signature is:", signtransbytes,
          " and address is ", address)
    signtrans = base64.b64encode(signtransbytes).decode('utf-8')
    if signtrans:
        print("Successfully signed the transaction and updated its signatures data.")
        sign_valid = transaction_manager.verify_sign(signtrans, public_key_bytes)
        if sign_valid:
            return transaction_manager.get_transaction_complete()
    else:
        print("Signing failed. No change made to transaction's signature data")
        return False


token_code = 'TSTTK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# def test_add_token():
#     add_wallet_request = {
#     "token_name": token_code,
#     "token_code": token_code,
#     "token_type": "1",
#     "first_owner": WALLET['address'],
#     "custodian": WALLET['address'],
#     "legal_doc": "",
#     "amount_created": 1000,
#     "tokendecimal": 2,
#     "disallowed_regions": [],
#     "is_smart_contract_token": False,
#     "token_attributes": {}
#     }

#     response = requests.post(NODE_URL + '/add-token', json=add_wallet_request)

#     unsigned_transaction = response.json()

#     signed_transaction = sign_transaction(WALLET, unsigned_transaction)
#     print(sign_transaction)

#     print('Test passed.')


if __name__ == '__main__':
    # test_add_token()
    pass