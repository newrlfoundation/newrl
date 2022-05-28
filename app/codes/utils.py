import hashlib
import sqlite3
import time

from ..constants import NEWRL_DB
from .clock.global_time import get_corrected_time_ms


def save_file_and_get_path(upload_file):
    if upload_file is None:
        return None
    file_location = f"/tmp/{upload_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(upload_file.file.read())
    return file_location


class BufferedLog():
    def __init__(self) -> None:
        self.buffer = ""
    
    def log(self, *text):
        for t in text:
            self.buffer += "\n" + str(t)
    
    def get_logs(self):
        return self.buffer


def get_time_ms():
    """Return time in milliseconds"""
    # return round(time.time() * 1000)
    return get_corrected_time_ms()


def get_person_id_for_wallet_address(wallet_address):
    hs = hashlib.blake2b(digest_size=20)
    hs.update(wallet_address.encode())
    person_id = 'pi' + hs.hexdigest()
    return person_id


def get_last_block_hash():
    """Get last block hash from db"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    last_block_cursor = cur.execute(
        'SELECT block_index, hash, timestamp FROM blocks ORDER BY block_index DESC LIMIT 1'
    )
    last_block = last_block_cursor.fetchone()
    con.close()

    if last_block is not None:
        return {
            'index': last_block[0],
            'hash': last_block[1],
            'timestamp': last_block[2]
        }
    else:
        return None