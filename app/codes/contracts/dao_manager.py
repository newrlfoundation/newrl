# class to create smart contract for creating stablecoins on Newrl
from .contract_master import ContractMaster
from ..db_updater import *
from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator
from ..kycwallet import generate_wallet_address


class dao_manager(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "dao_manager"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateondeploy(self, cur):
        pass

    def create(self, callparams,repo:FetchRepository):
        dao_params = input_to_dict(callparams)
        transaction_creator = TransactionCreator()
        # create wallet and pid for contract or dao_sc_main
        dao_sc_address = dao_params['dao_address']
        dao_wallet_address=dao_params['dao_wallet_address']
        dao_pid=repo.select_Query('person_id').add_table_name("person_wallet").where_clause('wallet_id',dao_wallet_address,1).execute_query_single_result({"wallet_id":dao_wallet_address})
        dao_person_id = dao_pid[0]


        # update dao db
        dao_name = dao_params['dao_name']
        dao_token_name=dao_params['token_name']
        founders_personid = json.dumps(dao_params['founders'])
        if(len(founders_personid)<3):
            return False
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": "dao_main",
            "sc_address": self.address,
            "data": {
                "dao_personid": dao_person_id,
                "dao_name": dao_name,
                "founder_personid": founders_personid,
                "dao_sc_address": dao_sc_address,
            }
        }
        txn_1=transaction_creator.transaction_type_8(sc_state_proposal1_data)
        # self.__create_dao_details(cur, dao_person_id, dao_name, founders_personid, dao_sc_address)
        # if DAO is of type Token based create SC token keeper for it

        # create contract instance for this new dao with params of dao sc main (contract table)
        contractparams = {}
        contractparams['status'] = 1
        contractparams['ts_init'] = time.mktime(datetime.datetime.now().timetuple())
        contractparams['address'] = dao_sc_address
        # ?
        contractparams['version'] = 1.0
        sdestr = 0
        # sdestr? TODO
        # sdestr = 0 if not contractparams['selfdestruct'] else int(contractparams['selfdestruct'])
        cstatus = 0 if not contractparams['status'] else int(contractparams['status'])
        cspecs = json.dumps(dao_params['contractspecs'])
        legpars = json.dumps(dao_params['legalparams'])
        # signatories founders wallet address as sign for DAO's setup and deploy? voraclestr ?
        # signstr = json.dumps(cspecs['signstr'])
        oraclestr = {}
        signstr = json.dumps(input_to_dict(cspecs)['signatories'])
        sc_state_proposal_data = {
            "operation": "save",
            "table_name": "contracts",
            "sc_address": self.address,
            "data": {
                "address": dao_sc_address,
                "creator": founders_personid,
                "ts_init": contractparams['ts_init'] ,
                "name": dao_params['dao_main_sc'],
                "version": dao_params['dao_main_sc_version'],
                "actmode": 0,
                "status": cstatus,
                "next_act_ts": 0,
                "signatories": signstr,
                "parent": 0,
                "oracleids": json.dumps(oraclestr),
                "selfdestruct": sdestr,
                "contractspecs": cspecs,
                "legalparams": legpars,
            }
        }
        txn=transaction_creator.transaction_type_8(sc_state_proposal_data)
        return [txn_1,txn]


    def alter(self, cur, callParamsip):
        pass

    def terminate(self, cur, callParamsip):
        pass

    # def __create_dao_details(self, cur, dao_personid, dao_name, founder_personid, dao_sc_address):
    #     cur.execute(f'''INSERT OR REPLACE INTO dao_main
    #                 (dao_personid, dao_name, founder_personid, dao_sc_address)
    #                 VALUES (?, ?, ?,?)''', (dao_personid, dao_name, founder_personid, dao_sc_address))
