from app.codes.helpers.FetchRespository import FetchRepository
from .dao_main_template import DaoMainTemplate
from ..db_updater import *

class membership_dao_role_vote(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None):
        self.template = 'membership_dao_role_vote'
        self.version='1.0.0'
        self.dao_type=1
        super().__init__(contractaddress)

    def vote_on_proposal(self, callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        #fetch proposal
        proposal_id = callparams['proposal_id']
        qparam = {"proposal_id": proposal_id}
        proposal_params_q = repo.select_Query(
            "params").add_table_name(
            "proposal_data").where_clause("proposal_id", proposal_id, 1).execute_query_single_result(qparam)
        if (proposal_params_q[0] is None):
            raise Exception("Proposal has no params")
        proposal_params = json.loads(proposal_params_q[0])
        roles_allowed = proposal_params["roles_allowed"]

        #fetch role
        wallet_address = callparams['function_caller'][0]['wallet_address']
        member_person_id = self.__get_pid_from_wallet_using_repo(repo, wallet_address)
        qparam = {"member_person_id": member_person_id}
        membership_role_q = repo.select_Query(
            "role").add_table_name(
            "dao_membership").where_clause("member_person_id", member_person_id, 1).execute_query_single_result(qparam)
        if (membership_role_q[0] is None):
            raise Exception("Member has no role")

        membership_role = membership_role_q[0]
        
        if not membership_role in roles_allowed:
            raise Exception("Member with his role cant vote for this proposal")
        return super().vote_on_proposal(callparamsip, repo)

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
