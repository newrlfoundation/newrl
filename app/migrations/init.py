import os
from app.config.constants import BLOCK_ARCHIVE_PATH, INCOMING_PATH, MEMPOOL_PATH, TMP_PATH, DATA_PATH, LOG_FILE_PATH
from ..migrations.init_db import init_db
from ..migrations.migrate_db import run_migrations


def init_newrl():
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    if not os.path.exists(LOG_FILE_PATH):
        os.mkdir(LOG_FILE_PATH)
    if not os.path.exists(MEMPOOL_PATH):
        os.mkdir(MEMPOOL_PATH)
    if not os.path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)
    if not os.path.exists(BLOCK_ARCHIVE_PATH):
        os.mkdir(BLOCK_ARCHIVE_PATH)
    if not os.path.exists(INCOMING_PATH):
        os.mkdir(INCOMING_PATH)

    # clear_db()
    init_db()

    # TODO - Run migrations
    run_migrations()

if __name__ == '__main__':
    init_newrl()