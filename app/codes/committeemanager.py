import sqlite3
import random
import logging

from ..nvalues import SENTINEL_NODE_WALLET
from ..constants import COMMITTEE_SIZE, MINIMUM_ACCEPTANCE_VOTES, NEWRL_DB, TIME_MINER_BROADCAST_INTERVAL_SECONDS
from .clock.global_time import get_corrected_time_ms
from .utils import get_last_block_hash
from app.codes.scoremanager import get_scores_for_wallets


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def weighted_random_choices(population, weights, k):
    if len(population) < k:
        raise Exception('Population less than selection count')
    
    selections = []

    while len(selections) < k:
        random.seed(0)
        choice = random.choices(population, weights=weights)[0]
        index = population.index(choice)
        selections.append(choice)
        del population[index]
        del weights[index]
    
    return selections


def get_miner_for_current_block(last_block=None):
    if last_block is None:
        last_block = get_last_block_hash()

    if not last_block:
        return {'wallet_address': SENTINEL_NODE_WALLET}

    committee_list = get_committee_for_current_block()

    if len(committee_list) < MINIMUM_ACCEPTANCE_VOTES:
        logger.info('Inadequate committee. Sentinel node is the miner.')
        return {'wallet_address': SENTINEL_NODE_WALLET}

    random.seed(last_block['index'])
    return random.choice(committee_list)

    # return committee_list[0]



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
        '''
        select wallet_address, network_address, last_broadcast_timestamp from miners
        join person_wallet on person_id = dest_person_id
        join trust_scores on wallet_address = wallet_id and last_broadcast_timestamp > ?
        where score > 0
        ''', (cutfoff_epoch, )).fetchall()
    # miner_cursor = cur.execute(
    #     '''SELECT wallet_address, network_address, last_broadcast_timestamp 
    #     FROM miners 
    #     WHERE last_broadcast_timestamp > ?
    #     ORDER BY wallet_address ASC''', (cutfoff_epoch, )).fetchall()
    miners = [dict(m) for m in miner_cursor]
    con.close()
    return miners

def get_committee_for_current_block(last_block=None):
    if last_block is None:
        last_block = get_last_block_hash()

    if not last_block:
        return [{'wallet_address': SENTINEL_NODE_WALLET}]

    random.seed(last_block['index'])

    miners = get_eligible_miners()

    if len(miners) == 0:
        logger.info("No committee for current block. Using sentinel node.")
        return [{'wallet_address': SENTINEL_NODE_WALLET}]

    committee_size = min(COMMITTEE_SIZE, len(miners))
    # committee = random.sample(miners, k=committee_size)
    miner_wallets = list(map(lambda m: m['wallet_address'], miners))
    weights = get_scores_for_wallets(miner_wallets)
    committee = weighted_random_choices(miners, weights, committee_size)
    return committee
