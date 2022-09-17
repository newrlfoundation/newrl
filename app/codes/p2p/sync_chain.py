import json
import logging
import random
import subprocess
import requests
import sqlite3
import time
import copy
import multiprocessing

from app.codes import blockchain
from app.codes.fs.archivemanager import get_block_from_archive
from app.codes.utils import get_last_block_hash
from app.ntypes import BLOCK_CONSENSUS_INVALID, BLOCK_CONSENSUS_NA, BLOCK_CONSENSUS_VALID, BLOCK_STATUS_INVALID_MINED, BLOCK_VOTE_INVALID, BLOCK_VOTE_VALID
from ..clock.global_time import get_corrected_time_ms
from app.codes.crypto import calculate_hash
from app.codes.minermanager import am_i_in_block_committee, am_i_in_current_committee, get_committee_for_current_block
from app.codes.p2p.outgoing import broadcast_receipt, broadcast_block
from app.codes.receiptmanager import check_receipt_exists_in_db, validate_receipt
# from app.codes.utils import store_block_proposal
from app.constants import COMMITTEE_SIZE, MINIMUM_ACCEPTANCE_VOTES, NETWORK_TRUSTED_ARCHIVE_NODES, NEWRL_PORT, REQUEST_TIMEOUT, NEWRL_DB
from app.codes.p2p.peers import get_peers

from app.codes.validator import validate_block, validate_block_data, validate_block_transactions, validate_receipt_signature
from app.codes.timers import TIMERS
from app.codes.fs.temp_manager import append_receipt_to_block_in_storage, check_receipt_exists_in_temp, get_blocks_for_index_from_storage, store_block_to_temp, store_receipt_to_temp
from app.codes.consensus.consensus import get_committee_consensus, validate_empty_block, validate_block_miner_committee, generate_block_receipt, \
    add_my_receipt_to_block, validate_receipt_for_committee
from app.migrations.init_db import revert_chain
from app.nvalues import SENTINEL_NODE_WALLET
from app.codes.timers import SYNC_STATUS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_blocks(block_indexes):
    blocks = []
    for block_index in block_indexes:
        block = get_block_from_archive(block_index)
        if block:
            blocks.append(block)
        else:
            break
    return blocks


def get_block_hashes(start_index, end_index):
    con = sqlite3.connect(NEWRL_DB)
    # con.row_factory = sqlite3.Row
    cur = con.cursor()

    blocks = cur.execute(
        '''
        SELECT block_index, hash, timestamp FROM 
        blocks 
        where block_index>=? and block_index < ?
        ''', (start_index, end_index, )).fetchall()

    results = []
    for row in blocks:
        block = {
            'index': row[0],
            'hash': row[1],
            'timestamp': row[2],
        }
        results.append(block)

    return results


def get_block(block_index):
    chain = blockchain.Blockchain()
    return chain.get_block(block_index)

def get_last_block_index():
    last_block = blockchain.get_last_block_index()
    return last_block


def receive_block(block):
    if SYNC_STATUS['IS_SYNCING']:
        logger.info('Syncing with network. Ignoring incoming block.')
        return
    block_index = block['index']
    if block_index > get_last_block_index() + 1:
        logger.info('Node not in sync. Cannot add block')
        # sync_chain_from_peers()
        return

    if blockchain.block_exists(block_index):
        logger.info('Block alredy exist in chain. Ignoring.')
        return False
    
    # Check block for index for index and hash already in temp. If yes append receipts from local block from to the received block
    logger.info(f'Received new block: {json.dumps(block)}')


    broadcast_exclude_nodes = block['peers_already_broadcasted'] if 'peers_already_broadcasted' in block else None
    original_block = copy.deepcopy(block)
    # Check for sentinel node empty block
    if validate_empty_block(block, check_from_sentinel_node=True):
        logger.info('Accepting timeout block from sentinel node')
        accept_block(block, block['hash'])
        broadcast_block(original_block)
        return

    # store_block_proposal(block)
    
    if not validate_block_miner_committee(block):
        # Store proposal to penalise false miner. But a dishonest node can flood with blocks
        # causing chain to grow a lot as a DoS attack
        return False


    consensus = get_committee_consensus(block)
    if consensus == BLOCK_CONSENSUS_VALID:
        logger.info('Received block is after consensus')
        if not validate_block(block):
            logger.info('Invalid block received after valid consensus. Committee maybe malicious. Ignoring.')
            # if am_i_in_block_committee(block['data']):
            #     logger.info('Sending receipts for invalid block.')
            #     receipt_for_invalid_block = generate_block_receipt(block['data'], vote=0)
            #     committee = get_committee_for_current_block()
            #     broadcast_receipt(receipt_for_invalid_block, committee)
            return False

        original_block = copy.deepcopy(block)
        accept_block(block, block['hash'])
        broadcast_block(original_block, exclude_nodes=broadcast_exclude_nodes)
    elif consensus == BLOCK_CONSENSUS_INVALID:
        if not validate_empty_block(block):
            logger.warn('Committee empty block received is not valid. Ignoring.')
            return False
        
        logger.info('Committee empty block received for invalid block proposal by valid miner. Accepting and broadcasting.')
        original_block = copy.deepcopy(block)
        if accept_block(block, block['hash']):
            broadcast_block(original_block)
    else:  # Consensus not available
        store_block_to_temp(block)
        if am_i_in_current_committee():
            if validate_block(block):
                my_receipt = add_my_receipt_to_block(block, vote=BLOCK_VOTE_VALID)
                consensus_adding_my_receipt = get_committee_consensus(block)
                if consensus_adding_my_receipt == BLOCK_CONSENSUS_VALID:
                    logger.info('Block satisfies valid consensus after adding my receipt. Accepting and broadcasting.')
                    original_block = copy.deepcopy(block)
                    if accept_block(block, block['hash']):
                        broadcast_block(original_block)
                elif consensus_adding_my_receipt == BLOCK_CONSENSUS_NA:
                    committee = get_committee_for_current_block()
                    broadcast_receipt(my_receipt, nodes=committee)
                else:  # Not possible
                    logger.warn('Unexpected behaviour after adding my valid vote. Consensus became invalid. Not broadcasting')
                    return False
            else:
                # Generate empty block. 
                chain = blockchain.Blockchain()
                block = chain.mine_empty_block(block_status=BLOCK_STATUS_INVALID_MINED)
                store_block_to_temp(block)
                my_receipt = generate_block_receipt(block, vote=BLOCK_VOTE_INVALID)
                store_receipt_to_temp(my_receipt)
                committee = get_committee_for_current_block()
                time.sleep(1)
                broadcast_receipt(my_receipt, nodes=committee)

    return
    #     else:
    #         committee = get_committee_for_current_block()
    #         if (len(committee) < MINIMUM_ACCEPTANCE_VOTES and
    #             block['data']['creator_wallet'] == SENTINEL_NODE_WALLET):
    #                 logger.info('Inadequate committee for block. Accepting from sentinel node.')
    #                 accept_block(block, block['hash'])
    #                 broadcast_block(original_block, exclude_nodes=broadcast_exclude_nodes)
    #                 return
    #         if my_receipt:
    #             logger.info('Broadcasting my receipt')
    #             broadcast_receipt(my_receipt, committee)
    #         logger.info('Stored block to temp')
    #         store_block_to_temp(block)
    
    # return True


def sync_chain_from_node(url, block_index=None):
    """Update local chain and state from remote node"""
    if block_index is None:
        response = requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT)
        their_last_block_index = int(response.text)
    else:
        their_last_block_index = block_index
    my_last_block = get_last_block_index()
    logger.info(f'I have {my_last_block} blocks. Node {url} has {their_last_block_index} blocks.')
    if my_last_block == their_last_block_index:
        logger.info('I am in sync with the node. Aborting sync.')
        return True

    if my_last_block < their_last_block_index - 1000:
        quick_sync(url + '/get-newrl-db')
        return True
    block_idx = my_last_block + 1
    block_batch_size = 100  # Fetch blocks in batches
    while block_idx <= their_last_block_index:
        blocks_to_request = list(range(block_idx, 1 + min(their_last_block_index, block_idx + block_batch_size)))
        blocks_request = {'block_indexes': blocks_to_request}
        logger.info(f'Asking block node {url} for blocks {blocks_request}')
        blocks_data = get_block_from_url_retry(url, block_idx, min(their_last_block_index, block_idx + block_batch_size))

        if blocks_data is None or len(blocks_data['blocks']) == 0:
            logger.warn('Could not get blocks aborting sync')
            return True  # To prevent revert

        for i in range(0, len(blocks_data['blocks']) - 1):
            block = blocks_data['blocks'][i]
            hash = blocks_data['hashes'][i]

            block_hash = calculate_hash(block)
            if hash != block_hash:
                logger.warn('Block hash does not match caculated hash. Aborting sync.')

            if not validate_block_data(block):
                logger.warn('Invalid block. Aborting sync.')
                return False
            else:
                logger.info('Adding block %d', block['index'])
                con = sqlite3.connect(NEWRL_DB)
                cur = con.cursor()
                blockchain.add_block(cur, block, hash)
                con.commit()
                con.close()

        block_idx += block_batch_size + 1

    return their_last_block_index


def sync_chain_from_peers(force_sync=False):
    global SYNC_STATUS
    logger.info(f'Syncing chain from peers with force_sync={force_sync} SYNC_STATUS={SYNC_STATUS}')
    if force_sync:
        SYNC_STATUS['IS_SYNCING'] = False
    if SYNC_STATUS['IS_SYNCING']:
        logger.info('Already syncing chain. Not syncing again.')
        return
    SYNC_STATUS['IS_SYNCING'] = True
    try:
        # peers = get_peers()
        # url, block_index = get_best_peer_to_sync(peers)
        url = get_majority_random_node()
        block_index = None

        if url:
            logger.info(f'Syncing from peer {url}')
            sync_success = sync_chain_from_node(url, block_index)
            if not sync_success:
                forking_block = find_forking_block(url)
                logger.info(f'Chains forking from block {forking_block}. Need to revert.')
                revert_chain(forking_block)
        else:
            logger.info('No node available to sync')
    except Exception as e:
        logger.info(f'Sync failed {e}')
    SYNC_STATUS['IS_SYNCING'] = False


def find_forking_block_with_majority():
    url = get_majority_random_node()
    forking_block = find_forking_block(url)
    return forking_block


# TODO - use mode of max last 
def get_best_peer_to_sync(peers, return_many=False):
    best_peers = []
    best_peer_value = 0

    peers = random.sample(peers, k=min(len(peers), 5))
    for peer in peers:
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            their_last_block_index = int(requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT).text)
            logger.info(f'Peer {url} has last block {their_last_block_index}')
            if their_last_block_index > best_peer_value:
                best_peers = [url]
                best_peer_value = their_last_block_index
            elif their_last_block_index == best_peer_value:
                best_peers.append(url)
        except Exception as e:
            logger.info(f'Error getting block index from peer at {url}')
    if return_many:
        return best_peers, best_peer_value
    else:
        best_peer = random.choice(best_peers)
        return best_peer, best_peer_value


def ask_peer_for_block(peer_url, block_index):
    blocks_request = {'block_indexes': [block_index]}
    logger.info(f'Asking block node {peer_url} for block {block_index}')
    try:
        blocks_data = requests.post(peer_url + '/get-blocks', json=blocks_request, timeout=REQUEST_TIMEOUT * 5).json()
        return blocks_data
    except Exception as e:
        logger.info(f'Could not get block {e}')
        return None


def ask_peers_for_block(block_index):
    peers = get_peers()
    peers = []
    for peer in peers:
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        block = ask_peer_for_block(url, block_index)
        if block is not None:
            return block
    return None


def accept_block(block, hash):
    global TIMERS

    # if hash is None:
    #     hash = calculate_hash(block['data'])
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    blockchain.add_block(cur, block['data'])
    con.commit()
    con.close()

    # block_timestamp = int(block['data']['timestamp'])
    # start_mining_clock(block_timestamp)
    TIMERS['mining_timer'] = None
    TIMERS['block_receive_timeout'] = None
    return True


def receive_receipt(receipt):
    logger.info('Recieved receipt: %s', receipt)

    receipt_data = receipt['data']
    block_index = receipt_data['block_index']

    if check_receipt_exists_in_temp(
            receipt_data['block_index'],
            receipt_data['block_hash'],
            receipt_data['wallet_address']
        ) or check_receipt_exists_in_db(
            receipt_data['block_index'],
            receipt_data['block_hash'],
            receipt_data['wallet_address']
        ):
        logger.info('Receipt already exists')
        return False

    last_block = get_last_block_hash()

    if not am_i_in_current_committee(last_block):
        logger.warn('I am not in committee. Cannot process receipt. Ignoring')
        return False

    if block_index != last_block['index'] + 1:
        logger.warn('Received receipt not for next block. Ignoring')
        return False
    
    if not validate_receipt(receipt):
        logger.info('Invalid receipt. Ignoring')
        return False

    if not validate_receipt_for_committee(receipt):
        logger.warn('Received receipt invalid for consensus. Ignoring')
        return False

    store_receipt_to_temp(receipt)
    blocks = get_blocks_for_index_from_storage(block_index)
    if len(blocks) != 0:
        blocks_appended = append_receipt_to_block_in_storage(receipt)
        for block in blocks_appended:
            consensus = get_committee_consensus(block)
            if not consensus == BLOCK_CONSENSUS_NA:
                logger.info(f"Consensus achieved {consensus} for block {block['index']} and hash {block['hash']}. Broadcasting to network.")
                original_block = copy.deepcopy(block)
                if not SYNC_STATUS['IS_SYNCING']:
                    accept_block(block, block['hash'])
                broadcast_block(original_block)
                break

    # committee = get_committee_for_current_block()
    # broadcast_receipt(receipt, committee)

    return True


def get_block_from_url_retry(url, start_index, end_index):
    response = None
    retry_count = 3
    while response is None:
        try:
            response = requests.post(
                    url + f'/get-archived-blocks?start_index={start_index}&end_index={end_index}',
                    timeout=3
                )
            if response.status_code != 200:
                return None
        except Exception as err:
            logger.info(f'Retrying block get {err}')
            if retry_count < 0:
                SYNC_STATUS['IS_SYNCING'] = False
                break
            retry_count -= 1
            time.sleep(1)
    blocks_data = response.json()
    return blocks_data


def get_block_tree_from_url_retry(url, start_index, end_index):
    response = None
    retry_count = 3
    while response is None or response.status_code != 200:
        try:
            response = requests.get(
                    url + f'/get-block-tree?start_index={start_index}&end_index={end_index}'
                )
        except Exception as err:
            logger.info(f'Retrying block get {err}')
            failed_for_invalid_block = True
            time.sleep(1)
            retry_count -= 1
            if retry_count == 0:
                break
    blocks_data = response.json()
    return blocks_data


def get_last_block_hash_from_url_retry(url):
    response = None
    # while response is None or response.status_code != 200:
    try:
        response = requests.get(
                url + '/get-last-block-hash',
                timeout=0.5
            )
        return response.json()['hash']
    except Exception as err:
        logger.info(f'Error getting block hash {err}')

    return None


def get_hash(peer):
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        hash = get_last_block_hash_from_url_retry(url)
        return hash, url

def get_majority_random_node():
    """Return a random node from the majority fork"""
    logger.info('Finding a majority node')
    peers = get_peers()
    hash_url_map = {}
    valid_peers = 0
    queried_peers = 0
    
    random.seed(get_corrected_time_ms())

    while len(hash_url_map) < COMMITTEE_SIZE and len(peers) > 0:
        peer_idx = random.choice(range(len(peers)))
        url = 'http://' + peers[peer_idx]['address'] + ':' + str(NEWRL_PORT)
        del peers[peer_idx]
        hash = get_last_block_hash_from_url_retry(url)
        if hash:
            valid_peers += 1
            if hash in hash_url_map:
                hash_url_map[hash].append(url)
                if len(hash_url_map[hash]) > COMMITTEE_SIZE * 0.6:
                    random_majority_node_url = random.choice(hash_url_map[hash])
                    logger.info(f'Majority hash is {hash} and a random url is {random_majority_node_url}')
                    return random_majority_node_url
            else:
                hash_url_map[hash] = [url]
        queried_peers += 1
        if valid_peers < COMMITTEE_SIZE and queried_peers > COMMITTEE_SIZE * 2:
            break    
    if valid_peers < COMMITTEE_SIZE:
        trusted_node = random.choice(NETWORK_TRUSTED_ARCHIVE_NODES)
        url = 'http://' + trusted_node + ':' + str(NEWRL_PORT)
        logger.info('Could not find a majority chain. Using archive node %s', url)
        return url

    logger.warn('Could not find a majority chain and enough peers responded with hash.')
    return None


# def get_majority_random_node_parallel():  # TODO - Need to fix for memory leakage
#     """Return a random node from the majority fork"""
#     logger.info('Finding a majority node')
#     peers = get_peers()
#     hashes = []
#     candidate_hash = ''
#     candidate_hash_count = 0
#     candidate_node_url = ''
#     random.seed(get_corrected_time_ms())
#     peers = random.sample(peers, k=min(len(peers), COMMITTEE_SIZE))

#     pool = multiprocessing.Pool(5)
#     hash_urls = pool.map(get_hash, peers)
#     for hash_url in hash_urls:
#         block_hash = hash_url[0]
#         url = hash_url[1]
#         if block_hash:
#             hashes.append(block_hash)
#             if block_hash == candidate_hash:
#                 candidate_hash_count += 1
#             else:
#                 candidate_hash_count -= 1
#             if candidate_hash_count < 0:
#                 candidate_hash = block_hash
#                 candidate_hash_count = 0
#                 candidate_node_url = url

#     logger.info(f'Majority hash is {candidate_hash} and a random url is {candidate_node_url}')
#     return candidate_node_url
#     # revert_chain(find_forking_block(candidate_node_url))
#     # sync_chain_from_node(candidate_node_url)


def find_forking_block(node_url):
    my_last_block_index = get_last_block_index()

    batch_size = 100
    start_idx = my_last_block_index - batch_size

    while start_idx >= 0:
        end_idx = start_idx + batch_size
        hash_tree = get_block_tree_from_url_retry(node_url, start_idx, end_idx)
        my_blocks = get_block_hashes(start_idx, end_idx)

        idx = end_idx - 1 - start_idx

        while idx >= 0:
            if hash_tree[idx]['hash'] == my_blocks[idx]['hash']:
                return idx + start_idx
            idx -= 1

        start_idx -= batch_size

    return 0


def quick_sync(db_url):
    """Copies the entire newrl.db from a peer. Unsecured."""
    downloaded_db_path = NEWRL_DB + ".DOWNLOADED"
    subprocess.call(["curl", "-o", downloaded_db_path, db_url])
    try:
        con = sqlite3.connect(downloaded_db_path)
        cur = con.cursor()
        blocks = cur.execute('SELECT block_index, hash FROM blocks ORDER BY block_index DESC LIMIT 1').fetchone()
        logger.info(f"Downloaded db from node with block {blocks[0]} and hash {blocks[1]}")
        con.close()
    except Exception as e:
        logger.info('Could not parse the downloaded DB' + str(e))
        return False

    try:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        existing_block = cur.execute('SELECT block_index, hash FROM blocks ORDER BY block_index DESC LIMIT 1').fetchone()
        logger.info(f"Existing db with block {existing_block[0]} and hash {existing_block[1]}")
        con.close()

        # Only copy if the downloaded db has more blocks than local
        if blocks[0] > existing_block[0]:
            subprocess.call(["mv", downloaded_db_path, NEWRL_DB])
    except Exception as e:
        logger.info('Could not query internal db. Using downloaded db' + str(e))
        subprocess.call(["mv", downloaded_db_path, NEWRL_DB])
