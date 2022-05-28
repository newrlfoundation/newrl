import json
import logging
import sqlite3
import requests
import socket
import subprocess
from threading import Thread
from app.codes.signmanager import sign_object
from app.codes.validator import validate_signature
from app.migrations.init import init_newrl
from ...constants import BOOTSTRAP_NODES, REQUEST_TIMEOUT, NEWRL_P2P_DB, NEWRL_PORT, MY_ADDRESS
from ..auth.auth import get_auth
from .utils import get_my_address


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_data = get_auth()


def clear_peer_db():
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS peers')
    con.commit()
    con.close()

def init_peer_db():
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS peers
                    (id text NOT NULL PRIMARY KEY,
                    address text NOT NULL 
                    )
                    ''')
    # Todo - link node to a person and add record in the node db
    con.commit()
    con.close()


def get_peers():
    peers = []
    con = sqlite3.connect(NEWRL_P2P_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    peer_cursor = cur.execute('SELECT * FROM peers').fetchall()
    peers = [dict(ix) for ix in peer_cursor]
    return peers


def add_peer(peer_address):
    peer_address = str(peer_address)

    if peer_address == '127.0.0.1':
        return {'address': peer_address, 'status': 'FAILURE'}

    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    try:
        logger.info('Adding peer %s', peer_address)
        # await register_me_with_them(peer_address)
        cur.execute('INSERT OR REPLACE INTO peers(id, address) VALUES(?, ?)', (peer_address, peer_address, ))
        con.commit()
    except Exception as e:
        logger.info('Did not add peer %s', peer_address)
        return {'address': peer_address, 'status': 'FAILURE', 'reason': str(e)}
    con.close()
    return {'address': peer_address, 'status': 'SUCCESS'}


def remove_peer(peer_id):
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    try:
        cur.execute('DELETE FROM peers where id = ?', (peer_id, ))
        con.commit()
    except Exception as e:
        print(e)
        return False
    con.close()
    return True


def clear_peers():
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    try:
        cur.execute('DELETE FROM peers')
        con.commit()
    except Exception as e:
        print(e)
        return False
    con.close()
    return True

def init_bootstrap_nodes():
    print(f'Initiating node discovery from bootstrap nodes: {BOOTSTRAP_NODES}')
    # clear_peer_db()
    init_peer_db()

    my_address = get_my_address()
    for node in BOOTSTRAP_NODES:
        if socket.gethostbyname(node) == my_address:
            continue
        logger.info(f'Boostrapping from node {node}')
        add_peer(node)
        try:
            response = requests.get('http://' + node + f':{NEWRL_PORT}/get-peers', timeout=REQUEST_TIMEOUT)
            their_peers = response.json()
        except Exception as e:
            their_peers = []
            print('Error getting nodes.', e)
        print(f'Peers from node {node} : {their_peers}')
        for their_peer in their_peers:
            add_peer (their_peer['address'])
    
    my_peers = get_peers()

    for peer in my_peers:
        address = peer['address']
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            response = register_me_with_them(address)
        except Exception as e:
            print(f'Peer unreachable, deleting: {peer}')
            remove_peer(peer['address'])
    return True


def register_me_with_them(address):
    auth_data = get_auth()
    logger.info(f'Registering me with node {address}')
    response = requests.post('http://' + address + f':{NEWRL_PORT}/add-peer', json=auth_data, timeout=REQUEST_TIMEOUT)
    return response.json()

def update_peers():
    my_peers = get_peers()
    my_address = get_my_address()

    for peer in my_peers:
        address = peer['address']
        logger.info('Updating peers: %s', address)
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            response = requests.post(
                'http://' + address + f':{NEWRL_PORT}/update-software',
                timeout=REQUEST_TIMEOUT
            )
            assert response.status_code == 200
            assert response.json()['status'] == 'SUCCESS'
        except Exception as e:
            print('Error updating software on peer', str(e))
    return True


def update_my_address():
    MY_ADDRESS = get_my_address()
    return True

def update_software(propogate):
    "Update the client software from repo"
    if propogate is True:
        logger.info('Propogaring update request to network')
        update_peers()

    logger.info('Getting latest code from repo')
    subprocess.call(["git", "pull"])
    subprocess.call(["sh", "scripts/install.sh"])
    init_newrl()


def validate_auth(auth):
    data = {
        'person_id': auth['person_id'],
        'wallet_id': auth['wallet_id'],
        'public': auth['public'],
    }
    signature = auth['signature']
    return validate_signature(
        data=data,
        public_key=auth['public'],
        signature=signature
    )


def call_api_on_peers(url):
    my_peers = get_peers()
    my_address = get_my_address()

    for peer in my_peers:
        address = peer['address']
        logger.info(f'Calling API {url} on peer {address}')
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            response = requests.get(
                'http://' + address + f':{NEWRL_PORT}' + url,
                timeout=REQUEST_TIMEOUT
            )
            assert response.status_code == 200
            assert response.json()['status'] == 'SUCCESS'
        except Exception as e:
            print(f'Error calling API on node {address}', str(e))


def remove_dead_peer(peer, my_address):
    address = peer['address']
    if socket.gethostbyname(address) == my_address:
        return
    try:
        response = requests.get(
            'http://' + address + f':{NEWRL_PORT}' + '/get-status',
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code != 200 or response.json()['up'] != True:
            remove_peer(peer['id'])
    except Exception as e:
        print('Removing peer', peer['id'])
        remove_peer(peer['id'])

def remove_dead_peers():
    my_peers = get_peers()
    my_address = get_my_address()

    for peer in my_peers:
        thread = Thread(target=remove_dead_peer, args=(peer, my_address))
        thread.start()
