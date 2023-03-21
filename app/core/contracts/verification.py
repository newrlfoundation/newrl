

import json
import math
from re import T
from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
from app.config.nvalues import ZERO_ADDRESS
from .contract_master import ContractMaster


class verification(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "verification"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    

    def add_verification(self,callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        asset_id = callparams['asset_id']
        verifier_address =  callparams['function_caller'][0]['wallet_address']

        if self._is_verification_present(asset_id,verifier_address,repo):
            raise Exception("Verification already present")
        
        doc_hash_list = callparams['doc_hash_list']
        doc_link_list = callparams['doc_link_list']
        outcome = callparams['outcome']
        remarks = callparams['remarks']
        deletable_after = callparams['deletable_after']
        asset_type = callparams['asset_type']

        data = {
             "address":self.address,
             "asset_id": asset_id,
             "asset_type":asset_type,
             "verifier_address": verifier_address,
             "outcome": outcome,
             "doc_hash_list": json.dumps(doc_hash_list),
             "doc_link_list": json.dumps(doc_link_list),
             "remarks":remarks,
             "deletable_after":deletable_after
        }

        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update)'''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": self.template,
            "sc_address": self.address,
            "data": data
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [sc_state_proposal1]

    def _is_verification_present(self, asset_id, verifier_address,repo:FetchRepository):
        qparam = {
          "asset_id":asset_id,
          "verifier_address":verifier_address  
        }  
        verification = repo.select_count().add_table_name("verification").where_clause("asset_id", asset_id, 1).and_clause("verifier_address",verifier_address,1).execute_query_multiple_result(qparam)
        if verification is None:
                raise Exception("Could not fetch verification")
        return verification[0][0] > 0
    
    def is_asset_valid(self,asset_id,asset_type):
         pass
    
