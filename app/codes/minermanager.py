"""Miner update functions"""
import sqlite3
import logging

from .p2p.peers import add_peer

from .p2p.utils import get_my_address
from ..constants import NEWRL_DB
from .clock.global_time import get_time_difference
from .auth.auth import get_wallet
from .signmanager import sign_transaction
from ..ntypes import TRANSACTION_MINER_ADDITION
from .utils import get_time_ms
from .transactionmanager import Transactionmanager
from .validator import validate
from .committeemanager import get_eligible_miners, get_miner_for_current_block, get_committee_for_current_block


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def miner_addition_transaction(wallet=None, my_address=None):
    if wallet is None:
        wallet = get_wallet()
    if my_address is None:
        my_address = get_my_address()
    timestamp = get_time_ms() - get_time_difference()
    transaction_data = {
        'timestamp': timestamp,
        'type': TRANSACTION_MINER_ADDITION,
        'currency': "NWRL",
        'fee': 0.0,
        'descr': "Miner addition",
        'valid': 1,
        'block_index': 0,
        'specific_data': {
            'wallet_address': wallet['address'],
            'network_address': my_address,
            'broadcast_timestamp': timestamp
        }
    }

    transaction_manager = Transactionmanager()
    transaction_data = {'transaction': transaction_data, 'signatures': []}
    transaction_manager.transactioncreator(transaction_data)
    transaction = transaction_manager.get_transaction_complete()
    signed_transaction = sign_transaction(wallet, transaction)
    return signed_transaction


def get_miner_status(wallet_address):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    miner_cursor = cur.execute(
        'SELECT wallet_address, network_address, last_broadcast_timestamp FROM miners WHERE wallet_address=?', (wallet_address, )).fetchone()
    if miner_cursor is None:
        return None
    miner_info = {
        'wallet_address': miner_cursor[0],
        'network_address': miner_cursor[1],
        'broadcast_timestamp': miner_cursor[2]
    }
    return miner_info


def get_my_miner_status():
    wallet = get_wallet()
    my_status = get_miner_status(wallet['address'])
    return my_status


def broadcast_miner_update():
    transaction = miner_addition_transaction()
    validate(transaction, propagate=True)


def get_committee_wallet_addresses():
    committee = get_committee_for_current_block()
    wallets = map(lambda c: c['wallet_address'], committee)
    return wallets


def should_i_mine(last_block=None):
    my_wallet = get_wallet()
    miner = get_miner_for_current_block(last_block=last_block)
    if miner['wallet_address'] == my_wallet['address']:
        logger.info("I am the miner for this block")
        return True
    return False


def am_i_in_current_committee(last_block=None):
    my_wallet_address = get_wallet()['address']
    committee = get_committee_for_current_block(last_block)

    found = list(filter(lambda w: w['wallet_address'] == my_wallet_address, committee))
    if len(found) == 0:
        return False
    return True


def get_miner_info():
    return {
        'current_block_miner': get_miner_for_current_block(),
        'current_block_committee': get_committee_for_current_block(),
        'eligible_miners': get_eligible_miners(),
    }


def add_miners_as_peers():
    miners = get_eligible_miners()

    for miner in miners:
        add_peer(miner['network_address'])


