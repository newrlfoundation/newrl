"""Committee selection code"""

from constants import MY_ADDRESS
from ..p2p.peers import get_peers


def get_current_committee():
    """Return the current committee members""" 
    # new_block_idx = last_block_idx + 1
    peers = get_peers()
    committee = peers[:5]  # TODO - Find the committe based on last block hash
    # use select_from function to select from peers
    return committee


def get_mining_node(committee, epoch):
    idx = epoch % len(committee)
    return committee[idx]


def am_i_miner():
    if get_mining_node()['address'] == MY_ADDRESS:
        return True
    return False