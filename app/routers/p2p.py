from random import randint
import sys
import threading
import uvicorn
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from app.codes.chainscanner import download_chain, download_state, get_transaction
from app.codes.clock.global_time import get_time_stats
from app.codes.p2p.peers import add_peer, clear_peers, get_peers, update_software
from app.codes.p2p.sync_chain import get_blocks, get_last_block_index, receive_block, receive_receipt, sync_chain_from_peers
from app.codes.p2p.sync_mempool import get_mempool_transactions, list_mempool_transactions, sync_mempool_transactions
from app.constants import NEWRL_PORT
from app.migrations.init_db import clear_db, init_db, revert_chain
from app.codes.p2p.peers import call_api_on_peers
from .request_models import BlockAdditionRequest, BlockRequest, ReceiptAdditionRequest, TransactionAdditionRequest, TransactionsRequest
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
def get_mempool_transactions_api(req: BlockRequest):
    return get_blocks(req.block_indexes)

@router.post("/receive-transaction", tags=[p2p_tag])
async def receive_transaction_api(req: TransactionAdditionRequest):
    return validate_transaction(req.signed_transaction, propagate=True)

@router.post("/receive-block", tags=[p2p_tag])
async def receive_block_api(req: BlockAdditionRequest):
    return receive_block(req.block)

@router.post("/receive-receipt", tags=[p2p_tag])
async def receive_receipt_api(req: ReceiptAdditionRequest):
    if receive_receipt(req.receipt):
        return {'status': 'SUCCESS'}
    else:
        return {'status': 'FAILURE'}

@router.get("/get-last-block-index", tags=[p2p_tag])
def get_last_block_index_api():
    return get_last_block_index()

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
