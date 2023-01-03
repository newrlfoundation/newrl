import base64
import ecdsa
from Crypto.Hash import keccak
import hashlib
import json


def get_address_from_public_key(public_key):
    public_key_bytes = bytes.fromhex(public_key)

    wallet_hash = keccak.new(digest_bits=256)
    wallet_hash.update(public_key_bytes)
    keccak_digest = wallet_hash.hexdigest()

    address = '0x' + keccak_digest[-40:]
    return address

def get_person_id_for_wallet_address(wallet_address):
    hs = hashlib.blake2b(digest_size=20)
    hs.update(wallet_address.encode())
    person_id = 'pi' + hs.hexdigest()
    return person_id
  
def b64_to_hex(b64_private):
  private_key_bytes = base64.b64decode(b64_private)
  wallet = {'public': None, 'private': None, 'address': None}
  key = ecdsa.SigningKey.from_string(
      private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
  key_bytes = key.to_string()

  private_key_hex = private_key_bytes.hex()
  public_key_hex = key_bytes.hex()
  wallet['address'] = get_address_from_public_key(public_key_hex)
  wallet['private'] = private_key_hex
  wallet['public'] = public_key_hex
  person_id = get_person_id_for_wallet_address(wallet['address'])
  auth_data = {
            'person_id': person_id,
            'wallet': wallet
        }
  return auth_data


private_key_b64 = input('Enter private key in b64: ')
print(json.dumps(b64_to_hex(private_key_b64)))