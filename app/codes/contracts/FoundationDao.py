from .dao_main_template import DaoMainTemplate
from ..db_updater import *
from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator


class FoundationDao(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None):
        self.template= 'FoundationDao'
        self.version='1.0.0'
        self.dao_type=1
        super().__init__(contractaddress)
    # def add_member(self, callparamsip, repo: FetchRepository):
    #     trxn=super(FoundationDao, self).add_member(callparamsip,repo)
    #     if(trxn is not None and len(trxn)>0):
    #         callparams=input_to_dict(callparamsip)
    #         role_member=callparams['role']
    #         dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
    #         sc_state_proposal1_data = {
    #             "operation": "save",
    #             "table_name": "membership_dao_role",
    #             "sc_address": self.address,
    #             "data": {
    #                 "address":self.address,
    #                 "dao_person_id": dao_pid,
    #                 "member_person_id": callparams['member_person_id'],
    #                 "role":int(role_member)
    #             }
    #         }
    #     transaction_creator = TransactionCreator()
    #     # role -1 is superuser
    #     # role 1 has veto power
    #     # role 2 normal user
    #     trxn.append(transaction_creator.transaction_type_8(sc_state_proposal1_data))
    #     return trxn

    # def initialize_membership(self, callparamsip, repo: FetchRepository):
    #     trxn=super(FoundationDao, self).initialize_membership(callparamsip,repo)
    #     if (trxn is not None and len(trxn) > 0):
    #         dao_params = repo.select_Query('founder_personid').add_table_name('dao_main').where_clause('dao_sc_address',
    #                                                                                                    self.address,
    #                                                                                                    1).execute_query_single_result(
    #             {'dao_sc_address': self.address})
    #         if dao_params is None:
    #             return []
    #         for i in json.loads(dao_params[0]):
    #             pid = self.__get_pid_from_wallet_using_repo(repo, i)
    #             dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
    #             qparam = {"dao_person_id": dao_pid, "member_person_id": pid}
    #             is_dao_exist = repo.select_count().add_table_name("membership_dao_role").where_clause("dao_person_id",
    #                                                                                              qparam[
    #                                                                                                  'dao_person_id'],
    #                                                                                              4).and_clause(
    #                 "member_person_id", qparam['member_person_id'], 4).execute_query_single_result(qparam)
    #             if (is_dao_exist[0] == 0):
    #                 sc_state_proposal1_data = {
    #                     "operation": "save",
    #                     "table_name": "membership_dao_role",
    #                     "sc_address": self.address,
    #                     "data": {
    #                         "address": self.address,
    #                         "dao_person_id": dao_pid,
    #                         "member_person_id": pid,
    #                         "role":-1
    #                     }
    #                 }
    #                 transaction_creator = TransactionCreator()
    #                 trxn.append(transaction_creator.transaction_type_8(sc_state_proposal1_data))
    #     return trxn

    def initialize_membership(self, callparamsip, repo: FetchRepository):
        trxn=[]
        dao_params=repo.select_Query('founder_personid').add_table_name('dao_main').where_clause('dao_sc_address',self.address,1).execute_query_single_result({'dao_sc_address':self.address})
        if dao_params is None:
            return []
        for i in json.loads(dao_params[0]):
            pid = self.__get_pid_from_wallet_using_repo(repo,i)
            callparams = input_to_dict(callparamsip)
            dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
            qparam = {"dao_person_id": dao_pid, "member_person_id": pid}
            is_dao_exist = repo.select_count().add_table_name("dao_membership").where_clause("dao_person_id",
                                                                                             qparam['dao_person_id'],
                                                                                             4).and_clause(
                "member_person_id", qparam['member_person_id'], 4).execute_query_single_result(qparam)
            # is_dao_exist = cur.execute(
            #     '''SELECT COUNT(*) FROM dao_membership WHERE dao_person_id LIKE ? AND member_person_id LIKE ?''',
            #     (dao_pid, callparams['member_person_id']))
            # is_dao_exist=is_dao_exist.fetchone()
            if (is_dao_exist[0] == 0):
                sc_state_proposal1_data = {
                    "operation": "save",
                    "table_name": "dao_membership",
                    "sc_address": self.address,
                    "data": {
                        "address":self.address,
                        "dao_person_id": dao_pid,
                        "member_person_id": pid,
                        "role": -1
                    }
                }
                transaction_creator = TransactionCreator()
                trxn.append(transaction_creator.transaction_type_8(sc_state_proposal1_data))
            else:
                return trxn
        return trxn

    def __get_pid_from_wallet_using_repo(self, repo: FetchRepository, address):
        if not address.startswith('ct'):
            spec = repo.select_Query('specific_data').add_table_name('wallets').where_clause('wallet_address', address,
                                                                                             1).execute_query_single_result(
                {'wallet_address': address})
            spec = input_to_dict(spec[0])
            if 'linked_wallet' in spec:
                address = spec['parentaddress']
        pid = repo.select_Query("person_id").add_table_name("person_wallet").where_clause("wallet_id", address,
                                                                                          1).execute_query_single_result(
            {"wallet_id": address})
        if pid is not None:
            return pid[0]
        return None