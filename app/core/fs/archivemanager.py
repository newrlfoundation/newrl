import json
import glob
import os
from app.config.constants import BLOCK_ARCHIVE_PATH
import shutil
import os
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_disk_getting_full():
    """
    Check if the disk is full. If yes, delete JSON files from the 'archive' folder.
    """
    # Get the free and total disk space in bytes
    disk = shutil.disk_usage("/")
    free_space = disk.free
    total_space = disk.total

    # Calculate the percentage of free disk space
    free_percent = (free_space / total_space) * 100

    # If the free percentage is less than 10%, delete JSON files from the 'archive' folder
    return free_percent < 5



def archive_block(block):
    block_index = block['index']
    new_file_name = f'{BLOCK_ARCHIVE_PATH}block_{block_index}.json'
    with open(new_file_name, 'w') as _file:
        json.dump(block, _file)
    return new_file_name


def get_block_from_archive(block_index):
    file_name = f'{BLOCK_ARCHIVE_PATH}block_{block_index}.json'
    try:
        with open(file_name, 'r') as _file:
            block = json.load(_file)
    except Exception as e:
        return None
    return block


def cleanup_old_archive_blocks(block_index):
    if not is_disk_getting_full():
        return
    logger.info('Disk is getting full. Cleaning up old blocks from archive folder.')
    blocks_to_persist = set()
    for i in range(max(block_index - 5000, 0), block_index):
        blocks_to_persist.add(f'{BLOCK_ARCHIVE_PATH}block_{i}.json')

    for block_file in glob.glob(f'{BLOCK_ARCHIVE_PATH}/block_*.json'):
        if block_file not in blocks_to_persist:
            os.remove(block_file)