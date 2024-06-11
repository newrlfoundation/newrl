"""Code for managing trust scores between two persons"""
import math
import sqlite3
from app.core.trustnet.kycwallet import get_person_id_for_wallet_from_db

from app.config.constants import INITIAL_NETWORK_TRUST_SCORE, NEWRL_DB
from app.config.nvalues import NETWORK_TRUST_MANAGER_PID
from ..db.db_updater import get_pid_from_wallet


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


def get_scores_for_wallets(wallet_addresses):
    trust_scores = []
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    for wallet_address in wallet_addresses:
        person_id = get_pid_from_wallet(cur, wallet_address)
        trust_score_cursor = cur.execute('''
            SELECT score FROM trust_scores where src_person_id=? and dest_person_id=?
            ''', (NETWORK_TRUST_MANAGER_PID, person_id)).fetchone()
                    
        if trust_score_cursor is None:
            existing_score = INITIAL_NETWORK_TRUST_SCORE
        else:
            existing_score = trust_score_cursor[0]
        trust_scores.append(existing_score)
    con.close()
    return trust_scores


def get_trust_score_for_wallets(source_wallet_id, destination_wallet_id):
    src_person_id = get_person_id_for_wallet_from_db(source_wallet_id)
    dest_person_id = get_person_id_for_wallet_from_db(destination_wallet_id)

    return get_trust_score(src_person_id, dest_person_id)


def get_incoming_trust_scores(destination_wallet_id):
    dst_person_id = get_person_id_for_wallet_from_db(destination_wallet_id)
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    trust_score_cursor = cur.execute('''
        SELECT src_person_id, score, last_time FROM trust_scores where dest_person_id=?
        ''', (dst_person_id, )).fetchall()

    con.close()

    return trust_score_cursor


def get_outgoing_trust_scores(source_wallet_id):
    src_person_id = get_person_id_for_wallet_from_db(source_wallet_id)
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    trust_score_cursor = cur.execute('''
        SELECT dest_person_id, score, last_time FROM trust_scores where src_person_id=?
        ''', (src_person_id, )).fetchall()

    con.close()

    return trust_score_cursor


def get_combined_scores(data):
    tscores = [item['score'] for item in data]
    stakes = [item['amount'] for item in data]
    normalised_tscores = normalise_scores(tscores)
    normalise_stake_scores = normalise_scores([stake/10**6 for stake in stakes])
    return [x + y for x, y in zip(normalise_stake_scores, normalised_tscores)]

def get_score_data_full(data):
    tscores = [item['score'] for item in data]
    stakes = [item['amount'] for item in data]
    normalised_tscores = normalise_scores(tscores)
    normalise_stake_scores = normalise_scores([stake/10**6 for stake in stakes])
    combined = [x + y for x, y in zip(normalise_stake_scores, normalised_tscores)]
    for i, item in enumerate(data):
      item['nrml_trust_score'] = normalised_tscores[i]
      item['nrml_stake_score'] = normalise_stake_scores[i]
      item['combined_score'] = combined[i]
    return data

def normalise_scores(scores):
    return log_normalize(scores)


def log_normalize(values):
    log_normalized_values = [math.log(value + 1) for value in values]
    return log_normalized_values

def sq_normalise(values):
    return [math.sqrt(x) for x in values]