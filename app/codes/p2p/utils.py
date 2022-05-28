import json
import sqlite3
import time
import requests
import socket

from ...constants import MY_ADDRESS_FILE, NEWRL_P2P_DB, TIME_MINER_BROADCAST_INTERVAL_SECONDS


def get_peers():
    peers = []
    con = sqlite3.connect(NEWRL_P2P_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    peer_cursor = cur.execute('SELECT * FROM peers').fetchall()
    peers = [dict(ix) for ix in peer_cursor]
    return peers


def get_my_address():
    current_time = int(time.time())
    try:
        with open(MY_ADDRESS_FILE, 'r') as f:
            my_address_data = json.load(f)
            if my_address_data['timestamp'] < current_time - TIME_MINER_BROADCAST_INTERVAL_SECONDS:
                raise Exception('Reset address')
            return my_address_data['address']
    except:
        ip = requests.get('https://api.ipify.org?format=json').json()['ip']
        with open(MY_ADDRESS_FILE, 'w') as f:
            data = {
                'address': ip,
                'timestamp': current_time
            }
            json.dump(data, f)
        return ip


def is_my_address(address):
    my_address = get_my_address()
    if socket.gethostbyname(address) == my_address:
        return True
    return False
