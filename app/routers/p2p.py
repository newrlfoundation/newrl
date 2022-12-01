from random import randint
import sys
import threading
import uvicorn
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from fastapi.responses import FileResponse

from app.limiter import limiter
from app.codes.aggregator import process_transaction_batch
from app.codes.blockchain import get_blocks_in_range

from app.codes.chainscanner import download_chain, download_state, get_transaction
from app.codes.clock.global_time import get_time_stats
from app.codes.dbmanager import get_or_create_db_snapshot
from app.codes.p2p.peers import add_peer, clear_peers, get_peers, update_software
from app.codes.p2p.sync_chain import find_forking_block_with_majority, get_block_hashes, get_blocks, get_last_block_index, get_majority_random_node, quick_sync, receive_block, receive_receipt, sync_chain_from_peers
from app.codes.p2p.sync_mempool import get_mempool_transactions, list_mempool_transactions, sync_mempool_transactions
from app.codes.p2p.peers import call_api_on_peers
from app.constants import NEWRL_DB
from .request_models import BlockAdditionRequest, BlockRequest, ReceiptAdditionRequest, TransactionAdditionRequest, TransactionBatchPayload, TransactionsRequest
from app.codes.auth.auth import get_node_wallet_address, get_node_wallet_public
from app.codes.validator import validate as validate_transaction
from app.codes.minermanager import get_miner_info

router = APIRouter()

p2p_tag = 'P2P'

@router.get("/get-node-wallet-address", tags=[p2p_tag])
def api_get_node_wallet_address():
    return {'wallet_address': get_node_wallet_address()}


@router.post("/list-mempool-transactions", tags=[p2p_tag])
def list_mempool_transactions_api():
    return list_mempool_transactions()

@router.post("/get-mempool-transactions", tags=[p2p_tag])
def get_mempool_transactions_api(req: TransactionsRequest):
    return get_mempool_transactions(req.transaction_codes)

@router.post("/get-blocks", tags=[p2p_tag])
def get_blocks_api(req: BlockRequest):
    return get_blocks(req.block_indexes)

@router.get("/get-archived-blocks", tags=[p2p_tag])
def get_archived_blocks_api(start_index: int, end_index: int):
    hashes = get_block_hashes(start_index, end_index + 1)
    hashes = list(map(lambda b: b['hash'], hashes))
    response = {
        'blocks': get_blocks(list(range(start_index, end_index + 1))),
        'hashes': hashes
    }
    return response

@router.get("/get-blocks-in-range", tags=[p2p_tag])
def get_blocks_in_range_api(start_index: int, end_index: int):
    return get_blocks_in_range(start_index, end_index)

@router.post("/receive-transaction", tags=[p2p_tag])
@limiter.limit("10/second")
async def receive_transaction_api(request: Request):
    signed_transaction = (await request.json())['signed_transaction']
    return validate_transaction(signed_transaction, propagate=True)

@router.post("/receive-transactions", tags=[p2p_tag])
@limiter.limit("100/minute")
async def receive_transactions_api(request: Request):
    request_body = await request.json()
    return process_transaction_batch(request_body['transactions'],
        request_body['peers_already_broadcasted'])

@router.post("/receive-block", tags=[p2p_tag])
@limiter.limit("100/minute")
async def receive_block_api(request: Request):
    request_body = await request.json()
    return receive_block(request_body['block'])

@router.post("/receive-receipt", tags=[p2p_tag])
@limiter.limit("100/minute")
async def receive_receipt_api(request: Request):
    request_body = await request.json()
    print('reciept_request_body', request_body)
    receipt = request_body['receipt']
    if receive_receipt(receipt):
        return {'status': 'SUCCESS'}
    else:
        return {'status': 'FAILURE'}

@router.get("/get-last-block-index", tags=[p2p_tag])
def get_last_block_index_api():
    return get_last_block_index()

@router.get("/get-random-majority-chain-peers", tags=[p2p_tag])
def get_majority_peers_api():
    # TODO - Return a list of majority nodes
    return get_majority_random_node(return_many=True)

@router.get("/find-forking-block-with-majority", tags=[p2p_tag])
def find_forking_block_with_majority_api():
    return find_forking_block_with_majority()

@router.get("/get-peers", tags=[p2p_tag])
def get_peers_api():
    return get_peers()

@router.get("/get-miners", tags=[p2p_tag])
def get_miners_api():
    return get_miner_info()

@router.post("/add-peer", tags=[p2p_tag])
def add_peer_api(req: Request, dns_address: str=None):
    if dns_address is None:
        return add_peer(req.client.host)
    else:
        return add_peer(dns_address)

@router.get("/get-newrl-db", tags=[p2p_tag], include_in_schema=False)
def get_newrldb_api():
    snapshot_file = get_or_create_db_snapshot()
    return FileResponse(snapshot_file)


@router.get("/quick-sync-db-from-node", tags=[p2p_tag], include_in_schema=False)
def get_newrldb_api(node_url: str):
    quick_sync(node_url + "/get-newrl-db")
