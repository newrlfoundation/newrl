from .contract_master import ContractMaster


class sc_test(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "sc_test"
        self.version = ""
        ContractMaster.__init__(self, self.template,self.version, contractaddress)

    def transfer_and_update(self,cur,params):
        transfer_proposal = self.getTrasnferRequest()
        return [transfer_proposal]

    def getTrasnferRequest(self):
        transfer_req = {
            "transaction": {
                "timestamp": 1656589367000,
                "trans_code": "8d93552b56448b176a6ea0690e728040f1f8a5ea",
                "type": 5,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": "",
                "valid": 1,
                "block_index": 0,
                "specific_data": {
                    "transfer_type": 1,
                    "asset1_code": "NWRL",
                    "asset2_code": "",
                    "wallet1": "ct0cd1b4c2a39c349762ee0fe94680f1bba9850852",
                    "wallet2": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
                    "asset1_number": 1,
                    "asset2_number": 0,
                    "additional_data": {}
                }
            },
            "signatures": []
        }
        return transfer_req
