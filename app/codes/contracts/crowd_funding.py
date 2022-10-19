from app.codes.contracts.contract_master import ContractMaster
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository


class crowd_funding(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "dex"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    
    def invest(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        unit_price = cspecs['unit_price']
        unit_currency = cspecs['unit_currency']
        
        value = callparams['value']

