

import math
from re import T
from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
from app.config.nvalues import ZERO_ADDRESS
from .contract_master import ContractMaster


class dex(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "alias"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    
    def add_entry(self,callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        wallet_address = callparams['address']
        alias = callparams['alias']

        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update) sample proposal'''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": "common_state",
            "sc_address": self.address,
            "data": {
                "address": self.address, 
                "identifier": wallet_address,
                "data": alias
            }
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [sc_state_proposal1]
    
