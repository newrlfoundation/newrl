import base64
import hashlib
import json
import ecdsa


def calculate_hash(block):
    """Calculate hash of a given block using sha256"""
    encoded_block = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(encoded_block).hexdigest()


def sign_object(private_key, data):
    """Sign an object using private key"""
    pvtkeybytes = base64.b64decode(private_key)
    msg = json.dumps(data).encode()
    sk = ecdsa.SigningKey.from_string(pvtkeybytes, curve=ecdsa.SECP256k1)
    msgsignbytes = sk.sign(msg)
    msgsign = base64.b64encode(msgsignbytes).decode('utf-8')
    return msgsign


#  TODO - Use till the nodes are identifiable. Random public-pvt combination
_public = "4trPBhDwdxWat2I8tE4Mj+7R6tiTJ+44GWtTdf5QpXnh/Ia1i5x4ETDufrCn3mjYN8gJs/w3iiMlDEmAAs7kvg=="
_private = "tW1Urj9jKj/i85R1P4HDSsaBi2WZDe74Ze6zxVxA1CI="
