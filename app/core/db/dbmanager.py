import random
import sqlite3
import os
import glob
import subprocess
import threading
import logging
from app.config.constants import SNAPSHOT_BLOCKS

from app.core.blockchain.blockchain import get_last_block_index

from app.config.constants import NEWRL_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

snapshot_schedule = {
    'next_snapshot': -1,
    'snapshot_creation_in_progress': False
}

def create_db_snapshot(suffix='.snapshot'):
    logger.info('Creating db snapshot')
    snapshot_file = NEWRL_DB + suffix
    con = sqlite3.connect(NEWRL_DB)
    bck = sqlite3.connect(snapshot_file)
    with bck:
        con.backup(bck)
    bck.close()
    con.close()
    logger.info('Db snapshot complete')
    return snapshot_file


def revert_to_last_snapshot():
    snapshots = glob.glob(NEWRL_DB + '.snapshot*')
    if len(snapshots) > 0:
        snapshot = snapshots[0]
        subprocess.call(["cp", snapshot, NEWRL_DB])

def check_snapshot_schedule(block_index):
    global snapshot_schedule
    if (
        snapshot_schedule['next_snapshot'] == -1 or 
        block_index >= snapshot_schedule['next_snapshot']):
        try:
            snapshot_last_block = get_last_block_index(NEWRL_DB + '.snapshot')
        except Exception as e:
            snapshot_last_block = 0
        db_last_block = get_last_block_index(NEWRL_DB)
        if db_last_block - snapshot_last_block < SNAPSHOT_BLOCKS:
            return False

    return True    
        

def create_block_snapshot(block_index):
    global snapshot_schedule
    snapshot_schedule['snapshot_creation_in_progress'] = True
    try:
        create_db_snapshot(f'.snapshot')
        snapshot_schedule['next_snapshot'] = block_index + random.randint(SNAPSHOT_BLOCKS-500, SNAPSHOT_BLOCKS)
        logger.info('Next snapshot creation scheduled for block %d', snapshot_schedule['next_snapshot'])
    except Exception as e:
        logger.error('Error during snapshot creation' + str(e))
    snapshot_schedule['snapshot_creation_in_progress'] = False
    return True
    # Set the next_snapshot schedule variable based on block size
    # Next snapshot increase ~ block size


def check_and_create_snapshot_in_thread(block_index):
    if not check_snapshot(block_index):
        logger.info("Snapshot creation check is False, will be checked again later")
        return False
    # thread = threading.Thread(target=create_block_snapshot,
    #     args = (block_index, ))
    # thread.start()
    # TODO - Check and enable threading
    return create_block_snapshot(block_index)

def check_snapshot(block_index):
    logger.info("Checking if snapshot can be created now")
    if snapshot_schedule['snapshot_creation_in_progress']:
        return False
    if not check_snapshot_schedule(block_index):
        return False 
    return True

def get_or_create_db_snapshot():
    snapshot_file = NEWRL_DB + '.snapshot'
    if os.path.isfile(snapshot_file):
        return snapshot_file
    
    create_db_snapshot()
    return snapshot_file


def get_snapshot_last_block_index():
    try:
        return get_last_block_index(NEWRL_DB + '.snapshot')
    except Exception as e:
        logger.warn('Could not get block index from snapshot')
        return None
    