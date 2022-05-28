"""Sign and validate signatures"""
import json
import base64
import ecdsa

from .transactionmanager import Transactionmanager, get_valid_addresses


def check_signing_address(transaction, address):
    """Check if an address is allowed to sign a transaction"""
    allowed_signing_addresses = get_valid_addresses(transaction)
    if address in allowed_signing_addresses:
        print(f"{address} is authorised to sign this transaction.")
        return True
    print(f"{address} is NOT authorised to sign this transaction.")
    return False


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


def sign_object(private_key, data):
    pvtkeybytes = base64.b64decode(private_key)
    msg = json.dumps(data).encode()
    sk = ecdsa.SigningKey.from_string(pvtkeybytes, curve=ecdsa.SECP256k1)
    msgsignbytes = sk.sign(msg)
    msgsign = base64.b64encode(msgsignbytes).decode('utf-8')
    return msgsign
