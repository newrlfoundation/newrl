"""Global constants in this file"""
import os

from .ntypes import NEWRL_TOKEN_CODE, NUSD_TOKEN_CODE

SOFTWARE_VERSION = "1.2.2.3"

NEWRL_ENV = os.environ.get('NEWRL_ENV')
IS_TEST = os.environ.get('NEWRL_TEST') == 'Y'

if NEWRL_ENV == 'testnet':
    BOOTSTRAP_NODES = ['bootstrap1-hsr-testnet.newrl.net']
    NETWORK_TRUSTED_ARCHIVE_NODES = ['archive1-hsr-testnet.newrl.net']
    NEWRL_PORT = 8090
    DATA_PATH = 'data_testnet/'
    print('Using testnet constants')
elif NEWRL_ENV == 'mainnet':
    BOOTSTRAP_NODES = ['bootstrap1-mainnet.newrl.net']
    NETWORK_TRUSTED_ARCHIVE_NODES = ['archive1-mainnet.newrl.net']
    NEWRL_PORT = 8456
    DATA_PATH = 'data_mainnet/'
    print('Using mainnet constants')
elif NEWRL_ENV == 'test':
    BOOTSTRAP_NODES = ['localhost']
    NETWORK_TRUSTED_ARCHIVE_NODES = ['localhost']
    NEWRL_PORT = 4018
    DATA_PATH = 'data_test/'
    print('Using test constants')
elif NEWRL_ENV == 'devnet':
    BOOTSTRAP_NODES = ['devnet.newrl.net']
    NETWORK_TRUSTED_ARCHIVE_NODES = ['devnetarchive1.newrl.net']
    NEWRL_PORT = 8420
    DATA_PATH = 'data_devnet/'
    print('Using devnet constants')
else:  # default ot devnet
    BOOTSTRAP_NODES = ['devnet.newrl.net']
    NETWORK_TRUSTED_ARCHIVE_NODES = ['devnetarchive1.newrl.net']
    NEWRL_PORT = 8420
    DATA_PATH = 'data_devnet/'
    print('Using devnet constants')

DATA_PATH = 'data_test/' if IS_TEST else DATA_PATH
LOG_FILE_PATH = DATA_PATH + 'logs/'
MEMPOOL_PATH = DATA_PATH + 'mempool/'
TMP_PATH = DATA_PATH + 'tmp/'
BLOCK_ARCHIVE_PATH = DATA_PATH + 'archive/'
INCOMING_PATH = DATA_PATH + 'tmp/incoming/'
NEWRL_DB = DATA_PATH + 'newrl.db'
NEWRL_P2P_DB = DATA_PATH + 'newrl_p2p.db'
STATE_FILE = 'state.json'
CHAIN_FILE = 'chain.json'
ALLOWED_CUSTODIANS_FILE = 'allowed_custodians.json'
DB_MIGRATIONS_PATH = 'app/migrations/migrations'
AUTH_FILE_PATH = DATA_PATH + '.auth.json'

REQUEST_TIMEOUT = 1
NEWRL_TOKEN = "newrl_token"
TREASURY = "treasury_address"
COINBASE_SC = "coinbase_sc_address"
TRANSPORT_SERVER = 'http://localhost:8095'

GLOBAL_INTERNAL_CLOCK_SECONDS = 5  # The time period between blocks
TIME_BETWEEN_BLOCKS_SECONDS = 10  # The time period between blocks
COMMITTEE_SIZE = 10
MINIMUM_ACCEPTANCE_VOTES = 6
MINIMUM_ACCEPTANCE_RATIO = 0.51
NO_BLOCK_TIMEOUT = 10  # No block received timeout in seconds
NO_RECEIPT_COMMITTEE_TIMEOUT = 10  # Timeout in seconds
NETWORK_BLOCK_TIMEOUT = 25
MAX_BROADCAST_NODES = 13
MEMPOOL_TRANSACTION_LIFETIME_SECONDS = 3600  # Mempool transactions will be removed after 1 hour
MAX_TRANSACTION_BATCH_SIZE = 500
MAX_TRANSACTION_SIZE = 4096
MIN_SYNC_INTERVAL_MS = 60000
MAX_RECEIPT_HISTORY_BLOCKS = 1000

# Variables
MY_ADDRESS_FILE = DATA_PATH + 'my_address.json'
TIME_DIFF_WITH_GLOBAL_FILE = DATA_PATH + 'time_diff.txt'
TIME_DIFF_WITH_GLOBAL = 0
MAX_ALLOWED_TIME_DIFF_SECONDS = 10
BLOCK_TIME_INTERVAL_SECONDS = TIME_BETWEEN_BLOCKS_SECONDS
BLOCK_RECEIVE_TIMEOUT_SECONDS = 5
TIME_MINER_BROADCAST_INTERVAL_SECONDS = 3600
MY_ADDRESS = ''

ALLOWED_FEE_PAYMENT_TOKENS = [NEWRL_TOKEN_CODE, NUSD_TOKEN_CODE]

MAX_NETWORK_TRUST_SCORE = 1000000
INITIAL_NETWORK_TRUST_SCORE = 100000
CUSTODIAN_OWNER_TYPE = 101
