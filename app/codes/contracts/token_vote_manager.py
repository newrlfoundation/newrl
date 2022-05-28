#class to manage token based voting
from .contract_master import ContractMaster
from ..db_updater import input_to_dict


class token_vote_manager(ContractMaster):
    codehash = ""    # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "token_manager"
        self.version = "1.0.0"
        ContractMaster.__init__(self, self.template, self.version, contractaddress)
    
    def updateondeploy(self, cur):
        pass

    

    
    def unlock_tokens(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        token_lock_data=cur.execute(f'''Select status as status from DAO_TOKEN_LOCK where person_id=? and dao_id=?''',(callparams['person_id'],callparams['dao_id']))
        status=token_lock_data['status']
        if(status is not None and status):
            pass
        else:
            return False


        '''
        TODO
        params : person_pid, dao_id,amount
        function : check if any proposals are pending ands if yes return False, else transfer back the amount
        '''
    


