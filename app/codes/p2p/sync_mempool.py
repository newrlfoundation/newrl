import json
import os
from app.constants import INCOMING_PATH, MEMPOOL_PATH, TMP_PATH
import requests

from app.codes.transactionmanager import Transactionmanager


def list_mempool_transactions():
    transaction_files = os.listdir(MEMPOOL_PATH)
    return transaction_files


def get_mempool_transactions(filenames):
    transactions = []
    for filename in filenames:
        with open(MEMPOOL_PATH + filename, "r") as transaction_file:
            transaction = json.load(transaction_file)
            transaction = {
                'filename': filename,
                'data': transaction
            }
            transactions.append(transaction)
    return transactions


def push_transactions(filenames):
    for filename in filenames:
        print('Pulling transaction:', filename)


def pull_transactions(filenames):
    # Todo - Make this call between nodes
    transactions = get_mempool_transactions(filenames)

    for transaction in transactions:
        filename = transaction['filename']
        data = transaction['data']
        print('Pulling transaction:', filename)
        validate_transaction(transaction)
        with open(MEMPOOL_PATH + filename, "w") as transaction_file:
            json.dump(data, transaction_file)


def sync_mempool_transactions():
    my_transactions = set(list_mempool_transactions())
    their_transactions = set(list_mempool_transactions())  # Todo - Make this call between nodes
    transactions_to_pull = their_transactions - my_transactions
    transactions_to_push = my_transactions - their_transactions

    if len(transactions_to_pull) != 0:
        pull_transactions(transactions_to_pull)
    else:
        print('No new transactions to pull')

    if len(transactions_to_push) != 0:
        push_transactions(transactions_to_push)
    else:
        print('No transactions to push')

    return {
        'pulled': transactions_to_pull,
        'pushed': transactions_to_push
    }


def validate_transaction(transaction):
    filename = INCOMING_PATH + transaction['filename']
    data = transaction['data']
    with open(filename, "w") as transaction_file:
            json.dump(data, transaction_file)
            
    tmtemp = Transactionmanager()
    trandata = tmtemp.loadtransactionpassive(filename)
    if not tmtemp.verifytransigns():
        print("Transaction id ", trandata['transaction']['trans_code'], " has invalid signatures")
        return False

    if not tmtemp.econvalidator():
        print("Economic validation failed for transaction ", trandata['transaction']['trans_code'])
        return False
    return True


def receive_transaction(transaction):
    transaction_code = transaction['transaction']['trans_code']
    with open(MEMPOOL_PATH + 'transaction-' + transaction_code + '.json', "w") as transaction_file:
        json.dump(transaction, transaction_file)