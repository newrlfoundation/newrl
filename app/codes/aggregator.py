from app.codes.validator import validate as validate_transaction
from app.codes.p2p.outgoing import propogate_transaction_batch_to_peers
from app.constants import MAX_TRANSACTION_BATCH_SIZE


def process_transaction_batch(transaction_list, exclude_nodes_broadcast=None):
    """
        Validate and save a batch of transactions to mempool
        Return the accepted transactions
    """
    if len(transaction_list) > MAX_TRANSACTION_BATCH_SIZE:
        return []
    new_transactions = []
    failed_transactions = []
    for transaction_data in transaction_list:
        print('Received transaction: ', transaction_data)
        validity = validate_transaction(transaction_data, propagate=False, validate_economics=True)
        if validity['valid'] and validity['new_transaction']:
            new_transactions.append(transaction_data)
        else:
            failed_transactions.append({
                'transaction_code': transaction_data['transaction']['trans_code'],
                'msg': validity['msg']
            })
    if len(new_transactions) > 0:
        propogate_transaction_batch_to_peers(new_transactions, exclude_nodes=exclude_nodes_broadcast)
    return [new_transactions, failed_transactions]
