import time
from app.codes.blockchain import get_last_block
from app.codes.chainscanner import get_transaction
from app.codes.p2p.sync_chain import receive_block

from app.tests.test_mempool import create_transaction

from .test_p2p import _receive_block
from .test_miner_committee import _add_test_miner
from ..codes.updater import mine, run_updater, start_mining_clock
from ..codes.minermanager import broadcast_miner_update
from fastapi.testclient import TestClient
from ..constants import BLOCK_TIME_INTERVAL_SECONDS

from ..main import app
from app.codes import updater

client = TestClient(app)


def test_mine():
    transaction = create_transaction(0)
    transaction_in_db = get_transaction(transaction['transaction']['trans_code'])
    assert transaction_in_db is None
    block = mine(add_to_chain=True)
    transaction_in_db = get_transaction(transaction['transaction']['trans_code'])
    assert transaction_in_db is not None
    