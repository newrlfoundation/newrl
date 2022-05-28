from .contract_master import ContractMaster
from ..db_updater import *

class newrl_treasury(ContractMaster):
    def __init__(self,contractaddress=None):
        self.template= "newrl_treasury"
        self.version="1.0.0"
        ContractMaster.__init__(self, self.template, self.version, contractaddress)
    
    def updateondeploy(self, cur):
        return True
    
    def distribute(self,cur):
        '''Distribute balance of fees earned to all owners of Newrl tokens proportionately'''
        return True