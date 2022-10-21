import json
import logging
import random
import time
import requests
from threading import Thread

from app.codes.p2p.packager import compress_block_payload

from ..clock.global_time import get_corrected_time_ms
from ...constants import IS_TEST, MAX_BROADCAST_NODES, NETWORK_TRUSTED_ARCHIVE_NODES, NEWRL_PORT, REQUEST_TIMEOUT, TRANSPORT_SERVER
from ..p2p.utils import get_my_address, get_peers
from ..p2p.utils import is_my_address


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def propogate_transaction_to_peers(transaction, exclude_nodes=None):
    if IS_TEST:
        return
    peers = get_peers()
    if exclude_nodes:
        peers = get_excluded_peers_to_broadcast(peers, exclude_nodes)

    node_count = min(MAX_BROADCAST_NODES, len(peers))
    peers = random.sample(peers, k=node_count)
    
    payload = {
        'signed_transaction': transaction,
        'peers_already_broadcasted': get_excluded_node_list(peers, exclude_nodes)
    }

    logger.info(f"Broadcasting transaction to peers {peers}")
    for peer in peers:
        if is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            thread = Thread(target=send_request, args = (url + '/receive-transaction', payload))
            thread.start()
        except Exception as e:
            pass
            # logger.warn(f"Error broadcasting transaction to peer: {url} Error - {str(e)}")


def propogate_transaction_batch_to_peers(transactions, exclude_nodes=None):
    if IS_TEST:
        return
    peers = get_peers()
    if exclude_nodes:
        peers = get_excluded_peers_to_broadcast(peers, exclude_nodes)

    node_count = min(MAX_BROADCAST_NODES, len(peers))
    peers = random.sample(peers, k=node_count)
    
    payload = {
        'transactions': transactions,
        'peers_already_broadcasted': get_excluded_node_list(peers, exclude_nodes)
    }

    logger.info(f"Broadcasting transaction to peers {peers}")
    for peer in peers:
        if is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            thread = Thread(target=send_request, args = (url + '/receive-transactions', payload))
            thread.start()
        except Exception as e:
            pass
            # logger.warn(f"Error broadcasting block to peer: {url} Error - {str(e)}")


def send_request_in_thread(url, data, as_json=True):
    thread = Thread(target=send_request, args = (url, data, as_json))
    thread.start()

def send_request(url, data, as_json=True):
    if IS_TEST:
        return
    try:
        if as_json:
            requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
        else:
            data = compress_block_payload(data)
            requests.post(url, data=data, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        pass
        # logger.warn(f"Error broadcasting block to peer: {url} Error - {str(e)}")

def send(payload):
    response = requests.post(TRANSPORT_SERVER + '/send', json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200:
        logger.error(f"Error sending")
    return response.text


def broadcast_receipt(receipt, nodes):
    logger.info('Broadcasting receipt to nodes %s', str(receipt))
    if IS_TEST:
        return

    for node in nodes:
        if 'network_address' not in node:
            continue
        if is_my_address(node['network_address']):
            continue
        url = 'http://' + node['network_address'] + ':' + str(NEWRL_PORT)
        logger.info(f"Sending receipt to node {url}")
        payload = {'receipt': receipt}
        try:
            thread = Thread(target=send_request, args=(url + '/receive-receipt', payload))
            thread.start()
        except Exception as e:
            pass
            # logger.warn(f"Error broadcasting receipt to peer: {url} Error - {str(e)}")


def broadcast_block(block_payload, nodes=None, exclude_nodes=None, send_to_archive=False):
    if IS_TEST:
        return
    if nodes:
        peers = []
        for node in nodes:
            if 'network_address' in node:
                peers.append({'address': node['network_address']})
            elif 'address' in node:
                peers.append({'address': node['address']})
        if len(peers) == 0:
            peers = get_random_peers(exclude_nodes)
    else:
        peers = get_random_peers(exclude_nodes)

    logger.info(f"Broadcasting block to peers {peers}")
    peers_i_am_broadcasting = get_excluded_node_list(peers, exclude_nodes)
    my_address = get_my_address()
    if my_address in peers_i_am_broadcasting:
        peers_i_am_broadcasting.remove(my_address)
    block_payload['peers_already_broadcasted'] = peers_i_am_broadcasting
    # TODO - Do not send to self
    for peer in peers:
        if 'address' not in peer or is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            # send_request_in_thread(url + '/receive-block', {'block': block_payload})
            send_request_in_thread(url + '/receive-block-binary', block_payload, as_json=False)
        except Exception as e:
            pass
            # logger.warn(f"Error broadcasting block-binary to peer: {url} Error - {str(e)}")
    if send_to_archive:
        for archive_node in NETWORK_TRUSTED_ARCHIVE_NODES:
            url = 'http://' + archive_node + ':' + str(NEWRL_PORT)
            send_request_in_thread(url + '/receive-block-binary', block_payload, as_json=False)
    return True


def get_excluded_peers_to_broadcast(peers, exclude_nodes):
    peers = filter(lambda p: p['address'] not in exclude_nodes, peers)
    return list(peers)


def get_random_peers(exclude_nodes=None):
    peers = get_peers()
    if exclude_nodes:
        peers = get_excluded_peers_to_broadcast(peers, exclude_nodes)
    node_count = min(MAX_BROADCAST_NODES, len(peers))
    random.seed(int(time.time()))
    peers = random.sample(peers, k=node_count)
    return peers


def get_excluded_node_list(new_nodes, already_broadcasted_nodes):
    new_node_addresses = list(map(lambda p: p['address'] if 'address' in p else None, new_nodes))
    if already_broadcasted_nodes:
        combined_list = new_node_addresses + already_broadcasted_nodes
    else:
        combined_list = new_node_addresses
    combined_list = list(set(combined_list))
    return combined_list
