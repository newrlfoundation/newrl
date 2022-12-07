"""Wallet manager"""
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import datetime
import base64
import sqlite3

from ..helpers.utils import get_time_ms
from app.config.constants import TMP_PATH, NEWRL_DB
from app.core.blockchain.transactionmanager import Transactionmanager



def get_address_from_public_key(public_key):
    public_key_bytes = bytes.fromhex(public_key)

    wallet_hash = keccak.new(digest_bits=256)
    wallet_hash.update(public_key_bytes)
    keccak_digest = wallet_hash.hexdigest()

    address = '0x' + keccak_digest[-40:]
    return address


def generate_wallet_address():
    private_key_bytes = os.urandom(32)
    key_data = {'public': None, 'private': None, 'address': None}
    key = ecdsa.SigningKey.from_string(
        private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
    key_bytes = key.to_string()

    private_key_hex = private_key_bytes.hex()
    public_key_hex = key_bytes.hex()
    key_data['address'] = get_address_from_public_key(public_key_hex)
    key_data['private'] = private_key_hex
    key_data['public'] = public_key_hex
    return key_data


def add_wallet(kyccustodian, kycdocs, ownertype, jurisd, public_key, wallet_specific_data={}):
    address = get_address_from_public_key(public_key)
    wallet = {
        'custodian_wallet': kyccustodian,
        'kyc_docs': kycdocs,
        'ownertype': ownertype,
        'jurisd': jurisd,
        'specific_data': wallet_specific_data,
        'wallet_address': address,
        'wallet_public': public_key,
    }

    trans = create_add_wallet_transaction(wallet)
    # ts = str(datetime.datetime.now())
    # file = TMP_PATH + "transaction-1-" + ts[0:10] + "-" + ts[-6:] + ".json"
    # transactionfile = trans.save_transaction_to_mempool(file)
    return trans


def generate_wallet(kyccustodian, kycdocs, ownertype, jurisd, wallet_specific_data={}):
    newkeydata = generate_wallet_address()
    wallet = {
        'custodian_wallet': kyccustodian,
        'kyc_docs': kycdocs,
        'ownertype': ownertype,
        'jurisd': jurisd,
        'specific_data': wallet_specific_data,
        'wallet_address': newkeydata['address'],
        'wallet_public': newkeydata['public'],
    }

    print("Now adding transaction")
    trans = create_add_wallet_transaction(wallet)
    ts = str(datetime.datetime.now())
    file = TMP_PATH + "transaction-1-" + ts[0:10] + "-" + ts[-6:] + ".json"
    transactionfile = trans.save_transaction_to_mempool(file)
    return transactionfile


def create_add_wallet_transaction(wallet):
    transaction_data = {
        'timestamp': get_time_ms(),
        'type': 1,
        'currency': 'NWRL',
        'fee': 0.0,
        'descr': 'New wallet',
        'valid': -1,
        'specific_data': wallet
    }
    transaction_data = {'transaction': transaction_data, 'signatures': []}
    transaction_manager = Transactionmanager()
    return transaction_manager.transactioncreator(transaction_data)


def get_digest(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_person_id_for_wallet_from_db(addressinput):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    wallet_cursor = cur.execute(
        'SELECT person_id FROM person_wallet WHERE wallet_id=?', (addressinput, )).fetchone()
    if wallet_cursor is None:
        return None
    pid = wallet_cursor[0]
    con.close()
    return wallet_cursor[0]
