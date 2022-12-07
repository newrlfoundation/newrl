
from fastapi.testclient import TestClient
from app.core.blockchain.blockchain import Blockchain, get_last_block_index

from app.core.consensus.consensus import generate_block_receipt
from app.core.fs.temp_manager import get_all_receipts_from_storage, store_receipt_to_temp
from app.core.p2p.sync_chain import accept_block
# from app.codes.receiptmanager import store_receipt_to_db
from app.core.blockchain.updater import mine, run_updater

from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def test_trust_score_update_for_block_miner():
    block_payload = run_updater(add_to_chain=False)
    assert block_payload is not None
    block = block_payload['data']
    receipt = block_payload['receipts'][0]
    assert block is not None
    assert receipt is not None

    # assert len(block['text']['previous_block_receipts']) == 0

    store_receipt_to_temp(receipt)
    
    accept_block(block_payload, block_payload['hash'])

    existing_receipts = get_all_receipts_from_storage(exclude_block_index=block['index'])
    # assert len(existing_receipts) == 1



