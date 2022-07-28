
from fastapi.testclient import TestClient
from app.codes.blockchain import get_last_block_index

from app.codes.consensus.consensus import generate_block_receipt
from app.codes.fs.temp_manager import check_receipt_exists_in_temp, remove_receipt_from_temp, store_receipt_to_temp
from app.codes.p2p.sync_chain import accept_block
from app.codes.receiptmanager import check_receipt_exists_in_db, get_receipts_included_in_block_from_db, store_receipt_to_db
from app.codes.updater import run_updater

from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def test_store_receipt_to_db():
    block_index = 345
    existing_receipts = get_receipts_included_in_block_from_db(block_index)
    
    receipt = generate_block_receipt({'index': block_index})
    store_receipt_to_db(receipt)
    new_receipts = get_receipts_included_in_block_from_db(block_index)
    assert len(existing_receipts) + 1 == len(new_receipts)


def test_block_receipt_addition():
    last_block_index = get_last_block_index()
    receipt = generate_block_receipt({'index': last_block_index})
    store_receipt_to_temp(receipt)
    block = run_updater()
    assert block['receipts'][0] is not None
    assert len(block['data']['text']['previous_block_receipts']) != 0

    accept_block(block, block['hash'])


def test_receipt_exist_store_delete():
    receipt = generate_block_receipt({'index': 100})
    block_hash = receipt['data']['block_hash']
    wallet_address = receipt['data']['wallet_address']
    remove_receipt_from_temp(100, block_hash, wallet_address)
    
    assert not check_receipt_exists_in_temp(100, block_hash, wallet_address)
    
    store_receipt_to_temp(receipt)

    assert check_receipt_exists_in_temp(100, block_hash, wallet_address)

    remove_receipt_from_temp(100, block_hash, wallet_address)

    assert not check_receipt_exists_in_temp(100, block_hash, wallet_address)


def test_check_receipt_exists_in_db():
    receipts = get_receipts_included_in_block_from_db(37)
    receipt = receipts[0]
    
    assert check_receipt_exists_in_db(
        receipt['data']['block_index'],
        receipt['data']['block_hash'],
        receipt['data']['wallet_address']
        )
    
    assert not check_receipt_exists_in_db(
        receipt['data']['block_index'] + 1,
        receipt['data']['block_hash'],
        receipt['data']['wallet_address']
        )