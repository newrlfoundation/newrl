# Abstract Class for creating DAOs
import json

from . import Utils
from .contract_master import ContractMaster
from .dao_main_template_validator import create_proposal, vote_on_proposal
from ..db_updater import *
from abc import ABCMeta, abstractmethod

import importlib


class DaoMainTemplate(ContractMaster):
    __metaclass__ = ABCMeta
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of

    # this class

    def __init__(self, contractaddress):
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    @abstractmethod
    def update_and_deploy(self):
        raise NotImplementedError("Must override updateAndDeploy")

    def create_proposal(self, cur, callparamsip):
        # Method For Creating Prosposal

        callparams = input_to_dict(callparamsip)
        callparams['address']=self.address
        # create_proposal(cur, callparams)
        dao_pid = get_pid_from_wallet(cur, self.address)
        # TODO max votes for now is hard coded
        cur.execute(f'''INSERT OR REPLACE INTO PROPOSAL_DATA
                    (dao_person_id, function_called,params,voting_start_ts,voting_end_ts,total_votes,status)
                    VALUES (?, ? ,? ,? ,? ,? ,? )''', (
            dao_pid, callparams['function_called'], json.dumps(callparams['params']), callparams['voting_start_ts'],
            callparams['voting_end_ts'], 10, 0))
        prop_id = cur.lastrowid
        response = {
            "status": 200,
            "proposal_id": prop_id
        }
        return response

    def vote_on_proposal(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        # ToDO Voting to be saved in
        callparams['address']=self.address
        # vote_on_proposal(cur, callparams)
        if self.dao_type==2 or self.valid_member(cur, callparams):
            
            member_pid = get_pid_from_wallet(cur,callparams['function_caller'][0]['wallet_address'])
            proposal_id=callparams['proposal_id']
            voter_db_data = cur.execute('''Select voter_data as "voter_data",yes_votes as "yes_votes",no_votes as "no_votes",abstain_votes as "abstain_votes",total_votes as "total_votes",function_called as "function_called"  from proposal_data where proposal_id = ?''', (proposal_id,))
            voter_db_data=voter_db_data.fetchone()


            # Initializing  the voter_db_data variable
            if (voter_db_data[0] is None):
                voter_db_data = ['{}', 0, 0, 0,voter_db_data[4],voter_db_data[5]]
            voter_data = input_to_dict(json.loads(voter_db_data[0]))
            yes_votes = voter_db_data[1]
            no_votes = voter_db_data[2]
            abstain_votes = voter_db_data[3]
            total_votes = voter_db_data[4]
            function_called = voter_db_data[5]
            weight=1
            if(self.dao_type==2):
                paramtopass={}
                paramtopass['dao_id']=self.address
                paramtopass['person_id']=member_pid
                weight=self.get_token_lock_amount(cur,json.dumps(callparamsip))
            if(self.duplicate_check(voter_db_data[0],member_pid)):


                if(callparams['vote']==-1):
                    no_votes=no_votes+weight
                elif(callparams['vote']==1):
                    yes_votes=yes_votes+weight
                else:
                    abstain_votes = abstain_votes +weight
                

                voter_data[member_pid]={"vote":callparams['vote'],"weight":weight}
                cur.execute(f'''update proposal_data set voter_data=?,yes_votes=?,no_votes=?,abstain_votes=?  where proposal_id = ?''',(json.dumps(voter_data),yes_votes,no_votes,abstain_votes,proposal_id))
        

            else:
                return False
        
            #get voting scheme params from dao params
            cspecs = input_to_dict(self.contractparams['contractspecs'])
            voting_schemes = cspecs['voting_schemes']
            voting_scheme_params = None
            voting_scheme_selected=None
            for method in voting_schemes:
                if(method['function'] == function_called):
                    voting_scheme_params = method['params']
                    voting_scheme_selected=method['voting_scheme']
            
            #get total votes, current yes and no votes from proposal
            voting_specs = {
                'voting_scheme_params': voting_scheme_params,
                'current_yes_votes': yes_votes,
                'current_no_votes': no_votes,
                'total_votes':total_votes
            }

            funct = getattr(Utils, voting_scheme_selected)
            voting_result = funct(cur, voting_specs)
            #check if any condition is met
                #if yes (-1 or 1)
                #update the db
                #execute the function
            if(voting_result == 1):
                cur.execute('''update proposal_data set status = ? where proposal_id= ?''',("accepted",callparamsip['proposal_id']))
                self.execute(cur, callparamsip)
            if(voting_result == -1):
                cur.execute('''update proposal_data set status = ? where proposal_id= ?''',("rejected",callparamsip['proposal_id']))
        
        return False

    def execute(self, cur, callparamsip):
        # proposal ( funct , paramsip) - votes status
        # Getting proposal Data
        callparams = input_to_dict(callparamsip)
        proposal = cur.execute('''select function_called,params from proposal_data where  proposal_id=?''',
                               ("".join(str(callparams['proposal_id'])),))
        proposal=proposal.fetchone()
        if (proposal is None):
            return False
        if self.check_status(cur,callparamsip):
            funct = getattr(self, proposal[0])
            funct(cur, proposal[1])
        else:
            return False

    def add_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        dao_pid = get_pid_from_wallet(cur, self.address)
        is_dao_exist = cur.execute(
            '''SELECT COUNT(*) FROM dao_membership WHERE dao_person_id LIKE ? AND member_person_id LIKE ?''',
            (dao_pid, callparams['member_person_id']))
        is_dao_exist=is_dao_exist.fetchone()
        if(is_dao_exist[0]==0):
            cur.execute('''INSERT OR REPLACE INTO dao_membership
                                (dao_person_id, member_person_id)
                                VALUES (?, ?)''', (dao_pid, callparams['member_person_id']))
            return {"status":200,"message":"Successfully added."}
        else:
            return {"status":500,"message":"Already exists."}

    def delete_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        dao_pid = get_pid_from_wallet(cur, self.address)
        # Sql code to update Membership table
        cur.execute('''DELETE FROM dao_membership 
                    WHERE dao_person_id= ? 
                    AND member_person_id= ? ''', (dao_pid, callparams['member_person_id']))
        return True

    def check_status(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        # if (cspecs['voting_scheme']):
        #     funct = getattr(Utils, cspecs['voting_scheme'])
        #     result = funct(cur, callparams)
        # else:
        #     result = Utils.voting_scheme_one(cur, callparams)
        # return result
        return True


    def valid_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        member_pid="".join(get_pid_from_wallet(cur,callparams['function_caller'][0]['wallet_address']))
        proposal = cur.execute('''Select count(*) from dao_membership where member_person_id like ?''', [member_pid])
        proposal=proposal.fetchone()
        if(proposal[0]==0):
            return False
        return True

    def duplicate_check(self,voter_data,member_pid):
        voter_data = input_to_dict(json.loads(voter_data))
        for voter in voter_data.keys():
            if(voter==member_pid):
                return False
        return True

    '''Token based methods'''
    # Token unique to DAO created via below method hence in template
    def issue_token(self, cur, callparamsip):
        '''
        TODO
        params : walletId , txnHash, amount
        function : check txn validity and issue dao tokens to that pid
        '''

        #call params
        callparams = input_to_dict(callparamsip)
        # Hash of Txn
        # transferTxn = callparams['transferTxn']

        recipient_address = callparams['recipient_address']
        amount = callparams['amount']
        # Stable Coin transfer from user to DAO
        transfer_tokens_and_update_balances(
            cur, recipient_address, self.address, 'NWRL', amount)
        #issue tokens
        dao_data=cur.execute(f'''Select dao_name as dao_name from dao_main where dao_sc_address=?''',[self.address])
        dao_data=dao_data.fetchone()
        token_code = dao_data[0]+'_token' #TODO fetch dao name
        tokendata={
        "tokenname": token_code,
        "tokencode" : token_code,
        "tokentype": '1',
        "tokenattributes": {},
        "first_owner": recipient_address,
        "custodian": self.address,
        "legaldochash": '',
        "amount_created": amount,
        "value_created": '',
        "disallowed": {},
        "sc_flag": False
    }
        # tokendata = {"tokencode": token_code,
        #              "first_owner": recipient_address,
        #              "custodian": self.address,
        #              "amount_created": int(amount * 100),
        #              "value_created": amount,
        #              "tokendecimal": 2
        #              }
        add_token(cur, tokendata)    
        pass


    def get_token_lock_amount(self, cur, callparamsip):
        '''
        TODO
        params : pid , daoId, proposal_id
        function : check if any balance, add this proposal for that token status entry with current balance
        '''         
        
        callparams = input_to_dict(callparamsip)
        dao_id = callparams['address']
        person_id=get_pid_from_wallet(cur,callparams['function_caller'][0]['wallet_address'])
        lock_data=cur.execute(f'''Select amount_locked from DAO_TOKEN_LOCK where person_id=? and dao_id=?''',[person_id,dao_id]).fetchone()
        return lock_data[0]
        #fetch current token value locked
        
    def set_price(self, cur, callapramsip):
        # To set the price at which token to be issued
        pass

    def lock_tokens(self, cur, callparamsip):
        '''
        TODO
        params : person_pid, dao_id, amount, txnHash (of transfer to dao)
        function : add a new row with pid and amount++
        '''

        callparams = input_to_dict(callparamsip)
        dao_id = self.address
        person_id = callparams['person_id']
        amount = callparams['amount']
        # proposal_id=callparams['proposal_id']
        proposal_id=None
        # Transfering Tokens from User To DAO
        dao_data=cur.execute(f'''Select dao_name as dao_name from dao_main where dao_sc_address=?''',[self.address])
        dao_data=dao_data.fetchone()
        token_code = dao_data[0]+'_token' #TODO fetch dao name
        transfer_tokens_and_update_balances(
            cur, callparams['wallet_address'], self.address, token_code, amount)
        lock_data = cur.execute(f'''Select dao_id as dao_id ,person_id as person_id, amount_locked as amount_locked from DAO_TOKEN_LOCK where person_id=? and dao_id=?''',
                                [person_id, dao_id]).fetchone()
        if lock_data is None:
            cur.execute(
                f'''Insert into DAO_TOKEN_LOCK (dao_id,person_id,amount_locked,wallet_address) values (?,?,?,?)''',
                (dao_id,person_id,amount,callparams['wallet_address']))
        else:
            amount = amount+ lock_data[2]
            cur.execute(f'''update DAO_TOKEN_LOCK set amount_locked=? where person_id=? and dao_id=? ''',[amount,person_id, dao_id])

        # update token stake table
        pass
    # def update_token_proposal_data(self, cur, callparamsip):
    #     #
    #     callparams = input_to_dict(callparamsip)
    #     dao_id = callparams['dao_id']
    #     person_id = callparams['person_id']
    #     proposal_id=callparams['proposal_id']
    #     amount_locked=callparams['amount_locked']
    #     lock_data = cur.execute(f'''Select proposal_list from DAO_TOKEN_LOCK where person_id=? and dao_id=?''',
    #                             [person_id, dao_id]).fetchone()
    #     if lock_data is None:
    #         cur.execute(
    #             f'''update  DAO_TOKEN_LOCK set proposal_list =? , amount_locked=? where person_id=? and dao_id=?''',
    #             (json.dumps({proposal_id})))
    #     else:
    #         flag=False
    #         lock_data=json.load(lock_data)
    #         for i in lock_data['proposal_list']:
    #             if(i==proposal_id):
    #                 flag=True
    #                 pass
    #         if not flag:
    #             lock_data['proposal_list'].append(proposal_id)
    #             cur.execute(
    #                 f'''update  DAO_TOKEN_LOCK set proposal_list =? , amount_locked=? where person_id=? and dao_id=?''',
    #                 (lock_data['proposal_list']))
    #     cur.execute()
    #
    #
    #     pass

