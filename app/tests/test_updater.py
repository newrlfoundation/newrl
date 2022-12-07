import time
from app.core.blockchain.blockchain import get_last_block
from app.core.consensus.consensus import generate_block_receipt
from app.core.crypto.crypto import calculate_hash
from app.core.p2p.sync_chain import receive_block

from app.tests.test_mempool import create_transaction

from .test_p2p import _receive_block
from .test_miner_committee import _add_test_miner
from ..core.blockchain.updater import create_empty_block_receipt_and_broadcast, mine, run_updater, start_mining_clock
from ..core.consensus.minermanager import broadcast_miner_update
from fastapi.testclient import TestClient
from app.config.constants import BLOCK_TIME_INTERVAL_SECONDS

from ..main import app
from app.core.blockchain import updater

client = TestClient(app)


def test_mine():
    # _add_test_miner(1)
    create_transaction(0)
    block = mine(add_to_chain=True)
    # start_mining_clock(int(get_last_block_hash()['timestamp']))


def test_receive():
    create_transaction(0)
    block = run_updater()
    assert block is not None
    receive_block(block)


def test_block_hash():
    create_transaction(0)
    block = mine()
    calculated_hash = calculate_hash(block['data'])
    assert block['hash'] == calculated_hash
    assert 'receipts' in block
    assert len(block['receipts']) == 1
    assert block['receipts'][0]['data']['block_hash'] == calculated_hash

    receipt = generate_block_receipt(block['data'])
    assert receipt['data']['block_hash'] == calculated_hash


def test_empty_block_mining():
    block_payload = create_empty_block_receipt_and_broadcast()
    assert block_payload['hash'] == calculate_hash(block_payload['data'])