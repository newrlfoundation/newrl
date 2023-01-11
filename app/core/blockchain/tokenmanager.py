# Python programm to create object that enables addition of a block

from ..helpers.utils import get_time_ms
from .transactionmanager import Transactionmanager


def create_token_transaction(token_data):
    transaction = {
        'timestamp': get_time_ms(),
        'type': 2,
        'currency': "NWRL",
        'fee': 0.0,
        'descr': "New token creation",
        'valid': 1,
        'block_index': 0,
        'specific_data': token_data
    }

    trans = Transactionmanager()
    transaction_data = {'transaction': transaction, 'signatures': []}
    transaction_data = trans.transactioncreator(transaction_data)
    return transaction_data
