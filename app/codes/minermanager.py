"""Miner update functions"""
import sqlite3
import random

from .p2p.peers import add_peer
from .clock.global_time import get_corrected_time_ms, get_time_difference
from ..nvalues import ASQI_WALLET
from .utils import get_last_block_hash
# from .p2p.outgoing import propogate_transaction_to_peers
from .p2p.utils import get_my_address
from ..constants import COMMITTEE_SIZE, IS_TEST, NEWRL_DB, TIME_MINER_BROADCAST_INTERVAL_SECONDS
from .auth.auth import get_wallet
from .signmanager import sign_transaction
from ..ntypes import TRANSACTION_MINER_ADDITION
from .utils import get_time_ms
from .transactionmanager import Transactionmanager
from .validator import validate


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


def get_eligible_miners():
    # last_block = get_last_block_hash()
    # last_block_epoch = 0
    # try:
    #     # Need try catch to support older block timestamps
    #     last_block_epoch = int(last_block['timestamp'])
    # except:
    #     pass
    # if last_block:
    #     cutfoff_epoch = last_block_epoch - TIME_MINER_BROADCAST_INTERVAL
    # else:
    #     cutfoff_epoch = 0
    # last_block_epoch = int(last_block['timestamp'])
    cutfoff_epoch = get_corrected_time_ms() - TIME_MINER_BROADCAST_INTERVAL_SECONDS * 2 * 1000

    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    miner_cursor = cur.execute(
        '''SELECT wallet_address, network_address, last_broadcast_timestamp 
        FROM miners 
        WHERE last_broadcast_timestamp > ?
        ORDER BY wallet_address ASC''', (cutfoff_epoch, )).fetchall()
    miners = [dict(m) for m in miner_cursor]
    con.close()
    return miners


def get_miner_for_current_block(last_block=None):
    if last_block is None:
        last_block = get_last_block_hash()

    if not last_block:
        return {'wallet_address': ASQI_WALLET}

    random.seed(last_block['index'])

    committee_list = get_committee_for_current_block()

    if len(committee_list) == 0:
        return {'wallet_address': ASQI_WALLET}

    return random.choice(committee_list)

    # return committee_list[0]


def get_committee_for_current_block(last_block=None):
    if last_block is None:
        last_block = get_last_block_hash()

    if not last_block:
        return [{'wallet_address': ASQI_WALLET}]

    random.seed(last_block['index'])

    miners = get_eligible_miners()

    if len(miners) == 0:
        return [{'wallet_address': ASQI_WALLET}]

    committee_size = min(COMMITTEE_SIZE, len(miners))
    committee = random.sample(miners, k=committee_size)
    return committee


def should_i_mine(last_block=None):
    my_wallet = get_wallet()
    miner = get_miner_for_current_block(last_block=last_block)
    if miner['wallet_address'] == my_wallet['address']:
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