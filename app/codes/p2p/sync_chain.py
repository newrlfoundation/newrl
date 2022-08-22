import json
import logging
import random
import subprocess
import requests
import sqlite3
import time
import copy

from app.codes import blockchain
from ..clock.global_time import get_corrected_time_ms
from app.codes.crypto import calculate_hash
from app.codes.minermanager import get_committee_for_current_block
from app.codes.p2p.outgoing import broadcast_receipt, broadcast_block
from app.codes.receiptmanager import check_receipt_exists_in_db
# from app.codes.utils import store_block_proposal
from app.constants import COMMITTEE_SIZE, MINIMUM_ACCEPTANCE_VOTES, NEWRL_PORT, REQUEST_TIMEOUT, NEWRL_DB
from app.codes.p2p.peers import get_peers

from app.codes.validator import validate_block, validate_block_data, validate_block_transactions, validate_receipt_signature
from app.codes.timers import TIMERS
from app.codes.fs.temp_manager import append_receipt_to_block_in_storage, check_receipt_exists_in_temp, get_blocks_for_index_from_storage, store_block_to_temp, store_receipt_to_temp
from app.codes.consensus.consensus import check_community_consensus, is_timeout_block_from_sentinel_node, validate_block_miner, generate_block_receipt, \
    add_my_receipt_to_block
from app.migrations.init_db import revert_chain
from app.nvalues import SENTINEL_NODE_WALLET
from app.codes.timers import SYNC_STATUS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_blocks(block_indexes):
    blocks = []
    for block_index in block_indexes:
        block = get_block(block_index)
        if block:
            blocks.append(get_block(block_index))
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
    
    logger.info(f'Received new block: {block}')


    broadcast_exclude_nodes = block['peers_already_broadcasted'] if 'peers_already_broadcasted' in block else None
    original_block = copy.deepcopy(block)
    if is_timeout_block_from_sentinel_node(block['data']):
        logger.info('Accepting timeout block from sentinel node')
        accept_block(block, block['hash'])
        broadcast_block(original_block)
        return

    # store_block_proposal(block)
    
    if not validate_block_miner(block['data']):
        # Store proposal to penalise false miner
        return False

    if not validate_block(block):
        logger.info('Invalid block. Sending receipts.')
        receipt_for_invalid_block = generate_block_receipt(block['data'], vote=0)
        committee = get_committee_for_current_block()
        broadcast_receipt(receipt_for_invalid_block, committee)
        return False

    if check_community_consensus(block):
        logger.info('Received block is after consensus. Accepting and broadcasting.')
        original_block = copy.deepcopy(block)
        accept_block(block, block['hash'])
        broadcast_block(original_block, exclude_nodes=broadcast_exclude_nodes)
    else:
        my_receipt = add_my_receipt_to_block(block)
        if check_community_consensus(block):
            logger.info('Block satisfies consensus after adding my receipt. Accepting and broadcasting.')
            original_block = copy.deepcopy(block)
            if accept_block(block, block['hash']):
                broadcast_block(original_block)
        else:
            committee = get_committee_for_current_block()
            if (len(committee) < MINIMUM_ACCEPTANCE_VOTES and
                block['data']['creator_wallet'] == SENTINEL_NODE_WALLET):
                    logger.info('Inadequate committee for block. Accepting from sentinel node.')
                    accept_block(block, block['hash'])
                    broadcast_block(original_block, exclude_nodes=broadcast_exclude_nodes)
                    return
            if my_receipt:
                logger.info('Broadcasting my receipt')
                broadcast_receipt(my_receipt, committee)
            logger.info('Stored block to temp')
            store_block_to_temp(block)
    
    return True


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

    quick_sync(url + '/get-newrl-db')
    return
    block_idx = my_last_block + 1
    block_batch_size = 50  # Fetch blocks in batches
    while block_idx <= their_last_block_index:
        failed_for_invalid_block = False
        blocks_to_request = list(range(block_idx, 1 + min(their_last_block_index, block_idx + block_batch_size)))
        blocks_request = {'block_indexes': blocks_to_request}
        logger.info(f'Asking block node {url} for blocks {blocks_request}')
        blocks_data = get_block_from_url_retry(url, blocks_request)

        for block in blocks_data:
            # block['index'] = block['block_index']
            # block['timestamp'] = int(block['timestamp'])
            hash = block['hash']  # TODO - Use calculate hash
            # hash = calculate_hash(block)
            # block.pop('hash', None)
            # block.pop('transactions_hash', None)
            # block.pop('block_index', None)
            for idx, tx in enumerate(block['text']['transactions']):
                specific_data = tx['transaction']['specific_data']
                while isinstance(specific_data, str):
                    specific_data = json.loads(specific_data)
                block['text']['transactions'][idx]['transaction']['specific_data'] = specific_data
                
                signatures = tx['transaction']['signatures']
                while isinstance(signatures, str):
                    signatures = json.loads(signatures)
                block['text']['transactions'][idx]['transaction']['signatures'] = signatures
                block['text']['transactions'][idx]['signatures'] = signatures

            if not validate_block_data(block):
                logger.info('Invalid block. Aborting sync.')
                failed_for_invalid_block = True
                return False
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            blockchain.add_block(cur, block, hash)
            con.commit()
            con.close()

        if failed_for_invalid_block:
            break

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
                # revert_chain(forking_block)
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
    if not validate_block_transactions(block['data']):
        logger.info('Transaction validation failed')
        return False

    # if hash is None:
    #     hash = calculate_hash(block['data'])
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    blockchain.add_block(cur, block['data'], hash)
    con.commit()
    con.close()

    # block_timestamp = int(block['data']['timestamp'])
    # start_mining_clock(block_timestamp)
    TIMERS['mining_timer'] = None
    TIMERS['block_receive_timeout'] = None
    return True


def receive_receipt(receipt):
    logger.info('Recieved receipt: %s', receipt)
    if not validate_receipt_signature(receipt):
        logger.info('Invalid receipt signature')
        return False

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

    # if blockchain.block_exists(block_index):
    #     return False

    store_receipt_to_temp(receipt)
    blocks = get_blocks_for_index_from_storage(block_index)
    if len(blocks) != 0:
        blocks_appended = append_receipt_to_block_in_storage(receipt)
        for block in blocks_appended:
            if check_community_consensus(block):
                original_block = copy.deepcopy(block)
                if not SYNC_STATUS['IS_SYNCING']:
                    accept_block(block, block['hash'])
                broadcast_block(original_block)

    # committee = get_committee_for_current_block()
    # broadcast_receipt(receipt, committee)

    return True


def get_block_from_url_retry(url, blocks_request):
    response = None
    retry_count = 3
    while response is None or response.status_code != 200:
        try:
            response = requests.post(
                    url + '/get-blocks',
                    json=blocks_request,
                    timeout=10
                )
        except Exception as err:
            logger.info(f'Retrying block get {err}')
            if retry_count < 0:
                SYNC_STATUS['IS_SYNCING'] = False
                break
            retry_count -= 1
            time.sleep(5)
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


def get_majority_random_node():
    """Return a random node from the majority fork"""
    logger.info('Finding a majority node')
    peers = get_peers()
    hashes = []
    candidate_hash = ''
    candidate_hash_count = 0
    candidate_node_url = ''
    random.seed(get_corrected_time_ms())
    peers = random.sample(peers, k=min(len(peers), COMMITTEE_SIZE))
    for peer in peers:
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        logger.info(f"Querying {url} for block hash")

        hash = get_last_block_hash_from_url_retry(url)
        if hash:
            hashes.append(hash)
            if hash == candidate_hash:
                candidate_hash_count += 1
            else:
                candidate_hash_count -= 1
            if candidate_hash_count < 0:
                candidate_hash = hash
                candidate_hash_count = 0
                candidate_node_url = url

    logger.info(f'Majority hash is {candidate_hash} and a random url is {candidate_node_url}')
    return candidate_node_url
    # revert_chain(find_forking_block(candidate_node_url))
    # sync_chain_from_node(candidate_node_url)


def find_forking_block(node_url):
    my_last_block_index = get_last_block_index()

    batch_size = 100
    start_idx = my_last_block_index - batch_size

    while start_idx >= 0:
        end_idx = start_idx + batch_size
        hash_tree = get_block_tree_from_url_retry(node_url, start_idx, end_idx)
        my_blocks = get_blocks(list(range(start_idx, end_idx)))

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
