
import json
import base64
import ecdsa


def sign_object(private_key, data):
    pvtkeybytes = bytes.fromhex(private_key)
    msg = json.dumps(data).encode()
    sk = ecdsa.SigningKey.from_string(pvtkeybytes, curve=ecdsa.SECP256k1)
    msgsignbytes = sk.sign(msg)
    msgsign = msgsignbytes.hex()
    return msgsign

def verify_sign(data, public_key,signature):
    public_key_bytes = bytes.fromhex(public_key)
    sign_trans_bytes = bytes.fromhex(signature)
    vk = ecdsa.VerifyingKey.from_string(
        public_key_bytes, curve=ecdsa.SECP256k1)
    message = json.dumps(data).encode()
    try:
        return vk.verify(sign_trans_bytes, message)
    except:
        return False


if __name__ == '__main__':
    WALLET = {
        "public": "dc0ac6d0a60d6d9f2c945b009472742e78f4a56be98a53fb9a72810a18a68727c64a58245f0ba5ad463ab86426c62222f8eef36cb9885823deb7d08d9dcbcee3",
        "private": "5e272e268e0fe09392b05007510f19670a5cffac797b4e081c53be37d0d558cb",
        "address": "0x57d6d216e5f6e0c837b23b5016ed363fe308e4cd"
    }
    WALLET = {"public": "09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee", "private": "d63e7ca37bcd6b43a6bdf281b2f9b4de7e64f027c0f741ffe12a105bf3955ec7", "address": "0x667663f36ac08e78bbf259f1361f02dc7dad593b"}
    data = {
                "block_index": 1,
                "block_hash": "8b99a6b9f9ffbf1439a3fbca036c5b7eb5fb16d813a448f2ea9b058da272f7a7",
                "vote": 9,
                "timestamp": 1663675898000,
                "wallet_address": "0x667663f36ac08e78bbf259f1361f02dc7dad593b"
            }
    msg = sign_object(WALLET['private'], data)
    msg = '165f0a0e2f79687a3093b9f3ed85177b4274413807babba6d12002b9ab54a46eece07decacd9a4e474b43d2cdda62e812519d8b8171419c1f714df850bd29309'
    print(verify_sign(data, WALLET['public'], msg))