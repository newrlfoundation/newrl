from fastapi.testclient import TestClient
import pytest

from app.codes.crypto import sign_object
from .test_miner_committee import _add_test_miner, clear_miner_db
from ..codes import updater
from ..codes.auth.auth import get_wallet
from ..migrations.init import init_newrl
from ..codes.minermanager import broadcast_miner_update

from ..main import app

client = TestClient(app)

init_newrl()

test_wallet = {
    "public": "wTxCEIm7oaKrYmmWIaeEcd4B49DsHb+D4VilmzhQZJCEmhT1XMFa/WmWoyBK3SRDuNGc9iOYdRBBCfeE0esH6A==",
    "private": "erMsIsopb9N6MYnDxvWtC+iaNb4PmQTY72D3jM5+lFE=",
    "address": "0x08a04d6f6a90248df7c392083c8eb52bba929597"
}


def _receive_block(block_index):
    response = client.post('/get-blocks', json={'block_indexes': [block_index]})
    assert response.status_code == 200
    blocks = response.json()
    assert len(blocks) == 0

    receipt_data = {
        "block_index": block_index,
        "block_hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "vote": 1
    }

    receipt = {
        "data": receipt_data,
        "public_key": test_wallet["public"],
        "signature": sign_object(test_wallet["private"], receipt_data)
    }
    
    block_payload = {
    "index": block_index,
    "hash": "0000be5942ea740bdfc244ca59aee40029d32e1bbc32cd5dc6fa2cd4012ba38c",
    "receipts": [
       receipt
    ],
    "data": {
        "index": block_index,
        "timestamp": "1645095917000",
        "proof": 27359,
        "text": {
            "transactions": [
                {
                    "timestamp": "1645095917000",
                    "trans_code": "a529a6c63c4b5480d88cd0b12e108e5340aaa25a",
                    "type": 1,
                    "currency": "NWRL",
                    "fee": 0,
                    "descr": "New wallet",
                    "valid": 1,
                    "specific_data": {
                        "custodian_wallet": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
                        "kyc_docs": [
                            {
                                "type": 1,
                                "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
                            }
                        ],
                        "ownertype": "1",
                        "jurisd": "910",
                        "specific_data": {},
                        "wallet_address": "0x515cf90af33acef220383a1d3f6813ac9a17f662",
                        "wallet_public": "Kymly4d62tafwLmioW2O3kWpHSLIJmYZCDQYz57oJofhmonuWFBfXZ8seSv83s/VlN7Oj1L/FhssAsxLIoDmoA=="
                    }
                }
            ],
            "signatures": [
                [
                    {
                        "wallet_address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
                        "msgsign": "gD1SAMhLqXqjHGVag2Gj3ypmepfmrwHkD7QbiD2y4u0vozG/Ib6Mh2P38dyMjcJzAF2nvcyegyNLwV1Ta0v/qA=="
                    }
                ]
            ]
        },
        "previous_hash": "0000ae69c361c65f088b52af8f5372f94f5f62d84f0980ea4c2cd71551206024",
        "receipts": [],
        'creator_wallet': get_wallet()['address']
    },
    }

    response = client.post('/receive-block', json={'block': block_payload})

    print(response.text)
    assert response.status_code == 200
    unsigned_transaction = response.json()

    response = client.post('/get-blocks', json={'block_indexes': [block_index]})
    blocks = response.json()
    assert len(blocks) == 1
    block = blocks[0]
    assert block['hash'] == block_payload['hash']
    

def test_block_receive():
    clear_miner_db()
    
    broadcast_miner_update()
    updater.mine(True)
    
    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    
    previous_block_index = int(response.text)
    _receive_block(previous_block_index + 1)
    
    response = client.get('/get-last-block-index')
    current_block_index = int(response.text)
    
    # Block index should've increased by 1
    assert current_block_index == (previous_block_index + 1)


def test_block_reject():
    """Expect block rejection from unexpected minors"""
    clear_miner_db()

    _add_test_miner(1)

    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    
    previous_block_index = int(response.text)
    with pytest.raises(Exception) as e_info:
        _receive_block(previous_block_index + 1)

    response = client.get('/get-last-block-index')
    current_block_index = int(response.text)
    
    # Block index should not increase
    assert current_block_index == previous_block_index