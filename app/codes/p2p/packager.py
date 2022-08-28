"""Library for packing and unpacking blocks for quick transport"""
import json
import zlib

def compress_signature(signature):
    return [signature['wallet_address'], signature['msgsign']]


def decompress_signature(compressed_sign):
    return {
        "wallet_address": compressed_sign[0],
        "msgsign": compressed_sign[1]
    }


def compress_block_receipt(receipt):
    return [
        receipt['data']['block_index'],
        receipt['data']['block_hash'],
        receipt['data']['vote'],
        receipt['data']['timestamp'],
        receipt['data']['wallet_address'],
        receipt['public_key'],
        receipt['signature'],
    ]


def decompress_block_receipt(compressed_receipt):
    return {
        "data": {
            "block_index": compressed_receipt[0],
            "block_hash": compressed_receipt[1],
            "vote": compressed_receipt[2],
            "timestamp": compressed_receipt[3],
            "wallet_address": compressed_receipt[4]
        },
        "public_key": compressed_receipt[5],
        "signature": compressed_receipt[6]
    }


def compress_block_transaction(transaction):
    signatures = list(
        map(lambda s: compress_signature(s), transaction['signatures']))
    return [
        transaction['transaction']['timestamp'],
        transaction['transaction']['trans_code'],
        transaction['transaction']['type'],
        transaction['transaction']['currency'],
        transaction['transaction']['fee'], transaction['transaction']['descr'],
        transaction['transaction']['valid'],
        transaction['transaction']['specific_data'], signatures
    ]

def decompress_block_transaction(compressed_transaction):
    signatures = list(map(lambda r: decompress_signature(r), compressed_transaction[8]))
    return {
            "transaction": {
                "timestamp": compressed_transaction[0],
                "trans_code": compressed_transaction[1],
                "type": compressed_transaction[2],
                "currency": compressed_transaction[3],
                "fee": compressed_transaction[4],
                "descr": compressed_transaction[5],
                "valid": compressed_transaction[6],
                "specific_data": compressed_transaction[7],
            },
            "signatures": signatures
        }


def compress_block_payload(block_payload):
    receipts = list(
        map(lambda r: compress_block_receipt(r), block_payload['receipts']))
    previous_block_receipts = list(
        map(lambda r: compress_block_receipt(r),
            block_payload['data']['text']['previous_block_receipts']))
    transactions = list(
        map(lambda r: compress_block_transaction(r),
            block_payload['data']['text']['transactions']))
    block_list = [
        block_payload['index'],
        block_payload['hash'],
        block_payload['data']['index'],
        block_payload['data']['timestamp'],
        block_payload['data']['proof'],
        transactions,
        previous_block_receipts,
        block_payload['data']['creator_wallet'],
        block_payload['data']['expected_miner'],
        block_payload['data']['committee'],
        block_payload['data']['previous_hash'],
        receipts,
        block_payload['software_version'],
        block_payload['peers_already_broadcasted'],
    ]
    # compressed_data = zlib.compress(json.dumps(block_list).encode("utf-8"))
    compressed_data = zlib.compress(json.dumps(block_payload).encode("utf-8"))
    return compressed_data

def decompress_block_payload(compressed_block):
    compressed_block = zlib.decompress(compressed_block)
    compressed_block = json.loads(compressed_block)
    return compressed_block
    transactions = list(map(lambda r: decompress_block_transaction(r), compressed_block[5]))
    previous_block_receipts = list(map(lambda r: decompress_block_receipt(r), compressed_block[6]))
    receipts = list(map(lambda r: decompress_block_receipt(r), compressed_block[11]))
    return {
        'index': compressed_block[0],
        'hash': compressed_block[1],
        'data': {
            'index': compressed_block[2],
            'timestamp': compressed_block[3],
            'proof': compressed_block[4],
            'text': {
                'transactions': transactions,
                'previous_block_receipts': previous_block_receipts
            },
            "creator_wallet": compressed_block[7],
            "expected_miner": compressed_block[8],
            "committee": compressed_block[9],
            "previous_hash": compressed_block[10]
        },
        'receipts': receipts,
        'software_version': compressed_block[12],
        'peers_already_broadcasted': compressed_block[13],
    }
