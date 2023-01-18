import json
import sqlite3

from app.core.helpers.utils import get_person_id_for_wallet_address
from app.config.constants import NEWRL_DB
from app.config.nvalues import CUSTODIAN_DAO_ADDRESS, CUSTODIAN_WALLET_LIST, DAO_MANAGER, ASQI_WALLET, FOUNDATION_WALLET, ASQI_DAO_ADDRESS, \
    ASQI_WALLET_DAO, FOUNDATION_WALLET_DAO, FOUNDATION_DAO_ADDRESS, MEMBER_WALLET_LIST


def migrate():
    print("Updating custodian Dao")
    update_custodian_dao_main()


def update_custodian_dao_main():
    """Update Custodian DAO."""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    updates_contract_specs = '{"dao_wallet_address":"0xce4b9b89efa5ee6c34655c8198c09494dc3d95bb","max_members":999999999,"max_voting_time":300000,"signatories":{"vote_on_proposal":null,"delete_member":[-1],"create_proposal":null,"add_member":[-1],"invest":[-1],"payout":[-1],"initialize_membership":null},"voting_schemes":[{"function":"add_member","voting_scheme":"voting_scheme_one","params":{"min_yes_votes":50},"veto_available":true,"veto_addresses":["0xf98eafede44ae6db2f6e6ad3762f5419ff1196d9","0x9dd356a2e4aa9a6c182d5f1e3f2e40ffa27bcfd5","0x47538e46a78e729079eb1614e2d6c387119c21fa","0x1342e0ae1664734cbbe522030c7399d6003a07a8","0x495c8153f65cf402bb0af6f93ba1eed4ace9aa7f","0x52c3a0758644133fbbf85377244a35d932443bf0","0x5017b00ced00b8b51d77d4569fa9d611b5b3b77a"]},{"function":"delete_member","voting_scheme":"voting_scheme_one","params":{"min_yes_votes":50},"veto_available":true,"veto_addresses":["0xf98eafede44ae6db2f6e6ad3762f5419ff1196d9","0x9dd356a2e4aa9a6c182d5f1e3f2e40ffa27bcfd5","0x47538e46a78e729079eb1614e2d6c387119c21fa","0x1342e0ae1664734cbbe522030c7399d6003a07a8","0x495c8153f65cf402bb0af6f93ba1eed4ace9aa7f","0x52c3a0758644133fbbf85377244a35d932443bf0","0x5017b00ced00b8b51d77d4569fa9d611b5b3b77a"]}]}'
    update_custodian_dao(cur, updates_contract_specs, CUSTODIAN_DAO_ADDRESS)

    con.commit()
    con.close()


def update_custodian_dao(cur, contract_specs,address):
    

    cur.execute(f'''UPDATE CONTRACTS SET contractspecs=? WHERE address=?''',
                (contract_specs, address))


    cur.execute(f'''UPDATE CONTRACTS SET name=? WHERE address=?''',
                ('membership_dao_ver1', address))   # migrate()
    pass
