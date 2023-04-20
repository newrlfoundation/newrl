import sqlite3
import random
import logging
import json

from app.config.nvalues import MIN_STAKE_AMOUNT, SENTINEL_NODE_WALLET, NETWORK_TRUST_MANAGER_PID
from app.config.constants import BLOCK_TIME_INTERVAL_SECONDS, COMMITTEE_SIZE, MINIMUM_ACCEPTANCE_VOTES, NEWRL_DB, TIME_MINER_BROADCAST_INTERVAL_SECONDS
from app.config.forks import FORK_BLOCK_INDEX_FIX_VALIDATOR_SELECTION_1_5_0
from ..clock.global_time import get_corrected_time_ms
from ..helpers.utils import get_last_block_hash
from app.core.trustnet.scoremanager import get_scores_for_wallets


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

miner_committee_cache = {
    'current_block_hash': '',
    'current_miner': SENTINEL_NODE_WALLET,
    'current_committee': [],
    'timestamp': 0
}


def get_number_from_hash(block):
    """
    Return a number from a string determinstically
    """
    # return hash(block_hash) % 1000000
    if block['index'] > 94000:
        seed = block['index'] + ord(block['hash'][0])
        seed = seed % 1000000
    else:
        seed = ord(block['hash'][0])
    return seed


def weighted_random_choices(population, weights, k, seed_prefix=0):
    if len(population) < k:
        raise Exception('Population less than selection count')
    random.seed(seed_prefix)
    v = [random.random() ** (1 / w) for w in weights]
    order = sorted(range(len(population)), key=lambda i: v[i])
    return [population[i] for i in order[-k:]]


def get_miner_for_current_block(last_block=None):
    global miner_committee_cache
    if last_block is None:
        last_block = get_last_block_hash()

    if not last_block:
        return {'wallet_address': SENTINEL_NODE_WALLET}

    if is_miner_committee_cached(last_block['hash']):
        logger.info(f'Using cached committee. Cache: {str(miner_committee_cache)}')
        return miner_committee_cache['current_miner']

    committee_list = get_committee_for_current_block()

    if len(committee_list) < MINIMUM_ACCEPTANCE_VOTES:
        logger.info('Inadequate committee. Sentinel node is the miner.')
        return {'wallet_address': SENTINEL_NODE_WALLET}

    random.seed(get_number_from_hash(last_block))
    miner = random.choice(committee_list)
    miner_committee_cache = {
        'current_block_hash': last_block['hash'],
        'current_miner': miner,
        'current_committee': committee_list,
        'timestamp': get_corrected_time_ms(),
    }
    return miner



def get_eligible_miners():
    last_block = get_last_block_hash()
    cutfoff_block = last_block['index'] - 1000

    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if cutfoff_block > FORK_BLOCK_INDEX_FIX_VALIDATOR_SELECTION_1_5_0:
        miner_cursor = cur.execute(
            '''
            select distinct m.wallet_address, network_address, last_broadcast_timestamp, block_index
            from miners m
            join person_wallet pw on m.wallet_address = pw.wallet_id
            join trust_scores ts on pw.person_id = ts.dest_person_id
            join stake_ledger sl on sl.wallet_address = m.wallet_address
            and m.block_index > ?
            and m.wallet_address != ?
            and sl.amount >= ?
            where ts.score > 0
            and ts.src_person_id = ?
            order by m.wallet_address asc
            ''', (cutfoff_block, SENTINEL_NODE_WALLET, MIN_STAKE_AMOUNT, NETWORK_TRUST_MANAGER_PID)).fetchall()
    else:
        miner_cursor = cur.execute(
        '''
        select distinct m.wallet_address, network_address, last_broadcast_timestamp, block_index
        from miners m
        join person_wallet pw on m.wallet_address = pw.wallet_id
        join trust_scores ts on pw.person_id = ts.dest_person_id
        join stake_ledger sl on sl.wallet_address = m.wallet_address
        and m.block_index > ?
        and m.wallet_address != ?
        and sl.amount >= ?
        where ts.score > 0
        order by m.wallet_address asc
        ''', (cutfoff_block, SENTINEL_NODE_WALLET, MIN_STAKE_AMOUNT, )).fetchall()
    # miner_cursor = cur.execute(
    #     '''SELECT wallet_address, network_address, last_broadcast_timestamp 
    #     FROM miners 
    #     WHERE last_broadcast_timestamp > ?
    #     ORDER BY wallet_address ASC''', (cutfoff_epoch, )).fetchall()
    miners = [dict(m) for m in miner_cursor]
    con.close()
    return miners

def get_committee_for_current_block(last_block=None):
    global miner_committee_cache
    if last_block is None:
        last_block = get_last_block_hash()

    if not last_block:
        return [{'wallet_address': SENTINEL_NODE_WALLET}]

    if is_miner_committee_cached(last_block['hash']):
        return miner_committee_cache['current_committee']

    miners = get_eligible_miners()

    if len(miners) < MINIMUM_ACCEPTANCE_VOTES:
        logger.info("Current committee cannot form consensus. Using sentinel node.")
        return [{'wallet_address': SENTINEL_NODE_WALLET}]

    committee_size = min(COMMITTEE_SIZE, len(miners))
    # committee = random.sample(miners, k=committee_size)
    miner_wallets = list(map(lambda m: m['wallet_address'], miners))
    weights = get_scores_for_wallets(miner_wallets)
    committee = weighted_random_choices(
        miners,
        weights,
        committee_size,
        get_number_from_hash(last_block))
    committee = sorted(committee, key=lambda d: d['wallet_address']) 
    return committee


def is_miner_committee_cached(last_block_hash):
    return False  # For testing
    global miner_committee_cache
    timestamp = get_corrected_time_ms()

    if (miner_committee_cache['current_block_hash'] == last_block_hash
        and miner_committee_cache['timestamp'] > timestamp - BLOCK_TIME_INTERVAL_SECONDS * 1000 / 2):
        return True
    return False


def get_committee_wallet_list_for_current_block():
    return list(map(lambda c: c['wallet_address'], get_committee_for_current_block()))