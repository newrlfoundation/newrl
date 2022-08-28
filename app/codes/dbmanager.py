import random
import sqlite3
import glob
import subprocess
import threading
import logging

from ..constants import NEWRL_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

snapshot_schedule = {
    'next_snapshot': -1
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
        subprocess.call(["mv", snapshot, NEWRL_DB])


def create_block_snapshot(block_index):
    if (
        snapshot_schedule['next_snapshot'] == -1 or 
        block_index == snapshot_schedule['next_snapshot']):
        # create_db_snapshot(f'.snapshot-{block_index}')
        create_db_snapshot(f'.snapshot')
        snapshot_schedule['next_snapshot'] = block_index + random.randint(500, 1000)
    # Set the next_snapshot schedule variable based on block size
    # Next snapshot increase ~ block size


def check_and_create_snapshot_in_thread(block_index):
    thread = threading.Thread(target=create_block_snapshot,
        args = (block_index, ))
    thread.start()