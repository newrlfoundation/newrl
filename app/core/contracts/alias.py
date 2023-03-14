

import math
from re import T
from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
from app.config.nvalues import ZERO_ADDRESS
from .contract_master import ContractMaster


class alias(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "alias"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    
    def add_entry(self,callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)

        alias = callparams['alias']
        wallet_address = callparams['function_caller'][0]['wallet_address']

        if not self._is_alias_unique(alias,repo):
            raise Exception("Contract Validation Failed, Alias already exists with given identifier")
        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update)'''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": self.template,
            "sc_address": self.address,
            "data": {
                "address": wallet_address, 
                "identifier": alias
            }
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [sc_state_proposal1]
    
    def _is_alias_unique(self, alias,repo:FetchRepository):
        qparam = {"identifier": alias}
        alias = repo.select_count().add_table_name("alias").where_clause(
                "identifier", qparam["identifier"], 1).execute_query_single_result(qparam)
        if alias is None or alias[0] == 0:
            return True
        else:
            return False
        
    def validate(self, txn_data, repo: FetchRepository):
        method = txn_data["function"]
        callparams = txn_data["params"]
        if (method == "add_entry"):
            callparams = input_to_dict(callparams)
            alias = callparams["alias"]
            if not self._is_alias_unique(alias, repo):
                raise Exception("Contract Validation Failed, Alias already exists with given identifier")

