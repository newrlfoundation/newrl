import time
from app.core.blockchain.blockchain import get_last_block
from app.core.blockchain.chainscanner import get_transaction
from app.core.p2p.sync_chain import get_blocks, receive_block

from app.tests.test_mempool import create_transaction

from .test_p2p import _receive_block
from .test_miner_committee import _add_test_miner
from ..core.blockchain.updater import mine, run_updater, start_mining_clock
from ..core.consensus.minermanager import broadcast_miner_update
from fastapi.testclient import TestClient
from app.config.constants import BLOCK_TIME_INTERVAL_SECONDS

from ..main import app
from app.core.blockchain import updater

client = TestClient(app)


def test_get_blocks():
    transaction = create_transaction(0)
    block = mine(add_to_chain=True)
    assert block is not None
    index = block['index']
    transaction_in_db = get_transaction(transaction['transaction']['trans_code'])
    assert transaction_in_db is not None
    blocks_from_db = get_blocks([index])
    assert len(blocks_from_db) == 1
    block_from_db = blocks_from_db[0]

    transactions = block_from_db['text']['transactions']
    assert len(transactions) == 1