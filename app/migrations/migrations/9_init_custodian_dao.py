import json
import sqlite3

from app.core.helpers.utils import get_person_id_for_wallet_address
from app.config.constants import NEWRL_DB
from app.config.nvalues import CUSTODIAN_DAO_ADDRESS, CUSTODIAN_WALLET_LIST, DAO_MANAGER, ASQI_WALLET, FOUNDATION_WALLET, ASQI_DAO_ADDRESS, \
    ASQI_WALLET_DAO, FOUNDATION_WALLET_DAO, FOUNDATION_DAO_ADDRESS, MEMBER_WALLET_LIST


def migrate():
    print("Creating custodian Dao")
    init_custodian_dao()


def init_custodian_dao():
    """Initialise Custodian DAO."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_custodian_dao(cur, CUSTODIAN_DAO_ADDRESS,
                         "CUSTODIAN_DAO", ASQI_WALLET)

    con.commit()
    con.close()


def create_custodian_dao(cur, address, name, wallet):
    address_signatories = CUSTODIAN_WALLET_LIST
    signatories = {"vote_on_proposal": None,
                   "delete_member": MEMBER_WALLET_LIST,
                   "create_proposal": None,
                   "add_member": MEMBER_WALLET_LIST,
                   "invest": [
                       -1
                   ],
                   "payout": [
                       -1
                   ],
                   "initialize_membership": None
                   }
    contract_specs = {"dao_wallet_address": wallet, "max_members": 999999999, "max_voting_time": 300000, "signatories": {"vote_on_proposal": None, "delete_member": [-1], "create_proposal": None, "add_member": [-1], "invest": [-1], "payout": [
        -1], "initialize_membership": None}, "voting_schemes": [{"function": "add_member", "voting_scheme": "voting_scheme_one", "params": {"min_yes_votes": 50}}, {"function": "delete_member", "voting_scheme": "voting_scheme_one", "params": {"min_yes_votes": 50}}]}
    query_params = (
        address,
        json.dumps(address_signatories),
        0,
        'CustodianDAO',
        '1.0.0',
        'hybrid',
        '1',
        None,
        json.dumps(signatories),
        None,
        '{}',
        '1',
        json.dumps(contract_specs),
        '{}'
    )
    dao_exists = cur.execute(f'''SELECT COUNT(*) FROM CONTRACTS WHERE ADDRESS=? AND NAME LIKE ? ''',
                             (address, 'FoundationDao'))
    dao_exists = dao_exists.fetchone()
    cur.execute(f'''INSERT OR IGNORE INTO CONTRACTS
        (address, creator, ts_init, 
        name, version, actmode, status,next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
    dao_main_param = {
        "address": DAO_MANAGER,
        "dao_personid": get_person_id_for_wallet_address(address),
        "founder_personid": json.dumps(address_signatories),
        "dao_sc_address": address,
        "dao_name": name
    }
    person_wallet_param = {"person_id": get_person_id_for_wallet_address(
        address), "wallet_id": address}
    cur.execute("INSERT OR IGNORE INTO dao_main (address, dao_personid, dao_name, founder_personid, dao_sc_address) VALUES "
                "(:address, :dao_personid, :dao_name, :founder_personid, :dao_sc_address)", dao_main_param)
    cur.execute("INSERT OR IGNORE INTO person_wallet (person_id, wallet_id) VALUES "
                "(:person_id, :wallet_id)", person_wallet_param)


if __name__ == '__main__':
    # migrate()
    pass
