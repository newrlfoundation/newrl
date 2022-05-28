import time
import sqlite3

from app.codes.blockchain import block_exists

from ..codes import updater
from ..codes.auth.auth import get_wallet
from ..codes.fs.mempool_manager import get_mempool_transaction
from ..codes.db_updater import update_wallet_token_balance
from fastapi.testclient import TestClient

from ..codes.fs.temp_manager import get_blocks_for_index_from_storage
from ..ntypes import NUSD_TOKEN_CODE
from ..constants import NEWRL_DB
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def test_block_exists():
    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    previous_block_index = int(response.text)

    assert block_exists(previous_block_index) == True
    assert block_exists(previous_block_index - 1) == True
    assert block_exists(previous_block_index + 1) == False

