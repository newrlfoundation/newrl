import json
from app.constants import BLOCK_ARCHIVE_PATH


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
