import json
import sqlite3

from app.core.helpers.utils import get_person_id_for_wallet_address
from app.config.constants import NEWRL_DB
from app.config.nvalues import DAO_MANAGER, ASQI_WALLET, FOUNDATION_WALLET, ASQI_DAO_ADDRESS, \
    ASQI_WALLET_DAO, FOUNDATION_WALLET_DAO, FOUNDATION_DAO_ADDRESS


def migrate():
    print("Migrating Foundation Dao")
    init_Foundation_Dao()


def init_Foundation_Dao():
    """Initialise Dao_Manager."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    create_foundation_dao(cur, ASQI_DAO_ADDRESS,"ASQI_DAO",ASQI_WALLET_DAO)
    create_foundation_dao(cur,FOUNDATION_DAO_ADDRESS,"NEWRL_DAO",FOUNDATION_WALLET_DAO)

    con.commit()
    con.close()


def create_foundation_dao(cur, address,name,wallet):
    address_signatories = [ASQI_WALLET_DAO, FOUNDATION_WALLET_DAO]
    signatories = {"vote_on_proposal": None,
                "delete_member": [
                    -1
                ],
                "create_proposal": None,
                "add_member": [
                    -1
                ],
                "invest": [
                    -1
                ],
                "payout": [
                    -1
                ],
                "initialize_membership":None
                   }
    contract_specs={"dao_wallet_address": wallet, "max_members": 999999999, "max_voting_time": 300000, "signatories": {"vote_on_proposal": None, "delete_member": [-1], "create_proposal": None, "add_member": [-1], "invest": [-1], "payout": [-1], "initialize_membership": None}, "voting_schemes": [{"function": "add_member", "voting_scheme": "voting_scheme_one", "params": {"min_yes_votes": 50}}, {"function": "delete_member", "voting_scheme": "voting_scheme_one", "params": {"min_yes_votes": 50}}]}
    query_params = (
        address,
        json.dumps(address_signatories),
        1648706655,
        'FoundationDao',
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
    dao_main_param={
        "address":DAO_MANAGER,
        "dao_personid":get_person_id_for_wallet_address(address),
        "founder_personid":json.dumps(address_signatories),
        "dao_sc_address":address,
        "dao_name":name
    }
    person_wallet_param={"person_id":get_person_id_for_wallet_address(address),"wallet_id":address}
    cur.execute("INSERT OR IGNORE INTO dao_main (address, dao_personid, dao_name, founder_personid, dao_sc_address) VALUES "
                "(:address, :dao_personid, :dao_name, :founder_personid, :dao_sc_address)",dao_main_param)
    cur.execute("INSERT OR IGNORE INTO person_wallet (person_id, wallet_id) VALUES "
                "(:person_id, :wallet_id)", person_wallet_param)


if __name__ == '__main__':
    # migrate()
    pass
