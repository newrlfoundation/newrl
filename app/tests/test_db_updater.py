import time
from app.core.blockchain.blockchain import get_last_block
from app.core.blockchain.chainscanner import get_transaction
from app.core.p2p.sync_chain import receive_block

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


def test_mine():
    transaction = create_transaction(0)
    transaction_in_db = get_transaction(transaction['transaction']['trans_code'])
    assert transaction_in_db is None
    block = mine(add_to_chain=True)
    transaction_in_db = get_transaction(transaction['transaction']['trans_code'])
    assert transaction_in_db is not None
    