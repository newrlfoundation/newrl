import json
import glob
import os
from app.config.constants import BLOCK_ARCHIVE_PATH


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
    return False  # Archive cleanup disabled 
    blocks_to_persist = set()
    for i in range(max(block_index - 10000, 0), block_index):
        blocks_to_persist.add(f'{BLOCK_ARCHIVE_PATH}block_{i}.json')

    for block_file in glob.glob(f'{BLOCK_ARCHIVE_PATH}/block_*.json'):
        if block_file not in blocks_to_persist:
            os.remove(block_file)