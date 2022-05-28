from fastapi.testclient import TestClient

from ..codes.fs.temp_manager import get_blocks_for_index_from_storage
from ..main import app
from ..codes.validator import validate_block, validate_receipt_signature
from ..codes.signmanager import sign_object

client = TestClient(app)


test_wallet = {
    "public": "wTxCEIm7oaKrYmmWIaeEcd4B49DsHb+D4VilmzhQZJCEmhT1XMFa/WmWoyBK3SRDuNGc9iOYdRBBCfeE0esH6A==",
    "private": "erMsIsopb9N6MYnDxvWtC+iaNb4PmQTY72D3jM5+lFE=",
    "address": "0x08a04d6f6a90248df7c392083c8eb52bba929597"
}


def test_validate_block_receipt():
    receipt_data = {
        "block_index": 241,
        "block_hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "vote": 1
    }

    receipt = {
        "data": receipt_data,
        "public_key": test_wallet["public"],
        "signature": sign_object(test_wallet["private"], receipt_data)
    }

    assert validate_receipt_signature(receipt) is True

    # Test receive receipt via API as well
    response = client.post("/receive-receipt", json={'receipt': receipt})
    print(response.text)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'SUCCESS'


def test_block_validation_success():
    block_data = {
        "index": 241,
        "timestamp": "2021-09-21 10:23:35.077991",
        "proof": 17672,
        "text": {
            "transactions": [
                {
                    "timestamp": "2021-09-21 10:23:34.861279",
                    "trans_code": "9258f94aa73746c9f39eefe192e6ac02d804cf1a",
                    "type": 4,
                    "currency": "NWRL",
                    "fee": 0.0,
                    "descr": "",
                    "valid": 1,
                    "specific_data": {
                        "asset1_code": 2,
                        "asset2_code": 7,
                        "wallet1": "0x308c4f49f25dd2213fabe814b82dd0797ef4fcf2",
                        "wallet2": "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
                        "asset1_number": 40152,
                        "asset2_number": 3
                    }
                }
            ],
            "signatures": [
                [
                    {
                        "wallet_address": "0x308c4f49f25dd2213fabe814b82dd0797ef4fcf2",
                        "msgsign": "5Zzbdwwgs987Jmd6UYmOw6a/YdcLWuc6i2CeijOCK89+4kKD/ykkU09/8XoTeTBi2UKAS0BIZJmi2N+2t04pQQ=="
                    },
                    {
                        "wallet_address": "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
                        "msgsign": "YssOvWMxJZsbrppfgRePKYAZy9R6DacOwfEypNKiCBiMKYKVfLQPHzcROCX4aBCjccNt36xol+9cORrc2Jw8og=="
                    }
                ]
            ]
        },
        "previous_hash": "00007f86fcdcfabc4a7b1d825abb006b381eca375e223f2b036f1f706053c8c0"
    }

    block_signature = {
        "public": test_wallet["public"],
        "msgsign": sign_object(test_wallet["private"], block_data)
    }
    receipt_data = {
        "block_index": 241,
        "block_hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "vote": 1
    }
    block = {
        "index": 241,
        "hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "data": block_data,
        "signature": block_signature,
        "receipts": [
            {
                "data": receipt_data,
                "public": test_wallet["public"],
                "signature": sign_object(test_wallet["private"], receipt_data)
            },
            {
                "data": receipt_data,
                "public": test_wallet["public"],
                "signature": sign_object(test_wallet["private"], receipt_data)
            }
        ]
    }

    # assert validate_block(block) is True


def test_block_receive_without_signatures():
    response = client.get('/get-last-block-index')
    assert response.status_code == 200

    previous_block_index = int(response.text)
    block_index = previous_block_index + 1

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
        'index': block_index,
        'hash': 'dd',
        "receipts": [
            receipt
        ],
        'data': {
          "creator_wallet": "0x20513a419d5b11cd510ae518dc04ac1690afbed6",
          "index": block_index,
          "previous_hash": "00007736868ba1a325c3ad8eba9bc02bba06fc315b0018f193d494dba67de542",
          "proof": 21054,
          "text": {
            "signatures": [
              [
                {
                  "msgsign": "C680g6RST4PtC7OoIKjTJSm+5mfVSCwM73SxEIOWfyYBzWpUA0as1qpRaDxKdfzx8xCuQn7mrOdyemT7M/e9PA==",
                  "wallet_address": "0xc29193dbab0fe018d878e258c93064f01210ec1a"
                }
              ]
            ],
            "transactions": [
              {
                "currency": "NUSD",
                "descr": "New wallet",
                "fee": 2,
                "specific_data": {
                  "custodian_wallet": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
                  "jurisd": "910",
                  "kyc_docs": [
                    {
                      "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
                      "type": 1
                    }
                  ],
                  "ownertype": "1",
                  "specific_data": {},
                  "wallet_address": "0xa64c2d51965e1bc9a7925c9b4e0e817d7b6bfd62",
                  "wallet_public": "T3v/sATHQtKY/kRnEU2ruKVekpAnAF/hCB4LqesSelQUCS13mXBvvri6WD58Q1jxeGbQc0pjl68JjIr86AHGiQ=="
                },
                "timestamp": 1647608631118,
                "trans_code": "ebc2838c215c92d874dcb387b2a9ca6d85e3daf7",
                "type": 1,
                "valid": 1
              }
            ]
          },
          "timestamp": 1647608631136
        }
    }

    client.post('/receive-block', json={'block': block_payload})

    response = client.post('/get-blocks', json={'block_indexes': [block_index]})
    blocks = response.json()
    assert len(blocks) == 1
    block = blocks[0]

    blocks_from_storage = get_blocks_for_index_from_storage(block['block_index'])
    assert len(blocks_from_storage) > 0
