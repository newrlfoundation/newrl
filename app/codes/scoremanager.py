"""Code for managing trust scores between two persons"""
import sqlite3

from app.constants import NEWRL_DB
from .transactionmanager import Transactionmanager
from .utils import get_time_ms
from ..ntypes import TRANSACTION_TRUST_SCORE_CHANGE


def update_score_transaction(personid1, address1, personid2, address2, new_score):
    transaction = {
        'timestamp': get_time_ms(),
        'type': TRANSACTION_TRUST_SCORE_CHANGE,
        'currency': "NWRL",
        'fee': 0.0,
        'descr': "Score update",
        'valid': 1,
        'block_index': 0,
        'specific_data': {
            "personid1": personid1,
            "address1": address1,
            "personid2": personid2,
            "address2": address2,
            "new_score": new_score
        }
    }

    transaction_manager = Transactionmanager()
    transaction_data = {'transaction': transaction, 'signatures': []}
    transaction_manager.transactioncreator(transaction_data)
    transaction_file = transaction_manager.save_transaction_to_mempool()
    return transaction_file


def get_trust_score(src_person_id, dest_person_id):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    trust_score_cursor = cur.execute('''
                SELECT score FROM trust_scores where src_person_id=? and dest_person_id=?
                ''', (src_person_id, dest_person_id))
    trust_score_res = trust_score_cursor.fetchone()
    con.close()
    if trust_score_res is None:
        return None
    else:
        return trust_score_res[0]