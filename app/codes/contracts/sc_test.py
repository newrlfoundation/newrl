from app.codes.helpers.TransactionCreator import TransactionCreator
from .contract_master import ContractMaster

class sc_test(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, address=None):
        self.template = "sc_test"
        self.version = ""
        ContractMaster.__init__(self, self.template,self.version, address)

    def transfer_and_update(self,params):
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": "NWRL",
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
            "asset1_number": 1,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal = transaction_creator.transaction_type_5(transfer_proposal_data)
    
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": "sc_test",
            "sc_address": self.address,
            "data": {
                "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
                "total_transfer_amount": 1
            }
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)

        return [transfer_proposal,sc_state_proposal1]
