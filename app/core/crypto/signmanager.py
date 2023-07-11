"""Sign and validate signatures"""
import json
import base64
import logging
import ecdsa

from app.core.blockchain.transactionmanager import Transactionmanager, get_valid_addresses

logger = logging.getLogger(__name__)

def check_signing_address(transaction, address):
    """Check if an address is allowed to sign a transaction"""
    allowed_signing_addresses = get_valid_addresses(transaction, address = address)
    if address in allowed_signing_addresses:
        logger.info(f"{address} is authorised to sign this transaction.")
        return True
    if 'fee_payer' in transaction and transaction['fee_payer'] == address:
        print(f"{address} is the fee payer for this transaction.")
        return True
    logger.warn(f"{address} is NOT part of allowed signatories to sign this transaction.")
    return True


def sign_transaction(wallet_data, transaction_data):
    """Sign a transaction using a given wallet"""
    address = wallet_data['address']
    private_key_bytes = bytes.fromhex(wallet_data['private'])
    public_key_bytes = bytes.fromhex(wallet_data['public'])
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
    signtrans = signtransbytes.hex()
    if signtrans:
        print("Successfully signed the transaction and updated its signatures data.")
        sign_valid = transaction_manager.verify_sign(signtrans, public_key_bytes)
        if sign_valid:
            return transaction_manager.get_transaction_complete()
    else:
        print("Signing failed. No change made to transaction's signature data")
        return False


def sign_object(private_key, data):
    pvtkeybytes = bytes.fromhex(private_key)
    msg = json.dumps(data).encode()
    sk = ecdsa.SigningKey.from_string(pvtkeybytes, curve=ecdsa.SECP256k1)
    msgsignbytes = sk.sign(msg)
    msgsign = msgsignbytes.hex()
    return msgsign

def verify_sign(data, signature, public_key):
    public_key_bytes = bytes.fromhex(public_key)
    sign_trans_bytes = bytes.fromhex(signature)
    vk = ecdsa.VerifyingKey.from_string(
        public_key_bytes, curve=ecdsa.SECP256k1)
    message = json.dumps(data).encode()
    try:
        return vk.verify(sign_trans_bytes, message)
    except:
        return False
