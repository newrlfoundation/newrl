# Abstract Class for creating DAOs
import json

from . import Utils
from .contract_master import ContractMaster
from .dao_main_template_validator import create_proposal, vote_on_proposal
from ..db_updater import *
from abc import ABCMeta, abstractmethod

import importlib

from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator


class DaoMainTemplate(ContractMaster):
    __metaclass__ = ABCMeta
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of

    # this class

    def __init__(self, contractaddress):
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)

    @abstractmethod
    def update_and_deploy(self):
        raise NotImplementedError("Must override updateAndDeploy")

    def create_proposal(self, callparamsip, repo: FetchRepository):
        # Method For Creating Prosposal
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)
        callparams['address'] = self.address
        # create_proposal(cur, callparams)
        # dao_pid = get_pid_from_wallet(cur, self.address)
        dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
        # qparam = {"tokencode": cspecs['token_name']} commented as token is not present with mem dao

        if self.dao_type == 2:
            qparam = {"tokencode": cspecs['token_code'],
                      "wallet_address": self.address}

            total_votes_curr = repo.select_sum("balance").add_table_name("balances").where_clause(
                "tokencode", qparam["tokencode"], 1).execute_query_single_result(qparam)
        else:
            qparam = {"dao_person_id": dao_pid}
            total_votes_curr = repo.select_count().add_table_name("dao_membership").where_clause(
                "dao_person_id", qparam["dao_person_id"], 1).execute_query_single_result(qparam)
        if total_votes_curr is None:
            total_votes_curr = 0
            logger.info("Zero Member for DAO "+self.address)
            return []
        else:
            total_votes_curr = total_votes_curr[0]

        # TODO max votes for now is hard coded
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": "PROPOSAL_DATA",
            "sc_address": self.address,
            "data": {
                "address": self.address,
                "dao_person_id": dao_pid,
                "function_called": callparams['function_called'],
                "params": json.dumps(callparams['params']),
                "voting_start_ts": callparams['voting_start_ts'],
                "voting_end_ts": callparams['voting_end_ts'],
                "total_votes": total_votes_curr,
                "status": 0
            }
        }
        # cur.execute(f'''INSERT OR REPLACE INTO PROPOSAL_DATA
        #             (dao_person_id, function_called,params,voting_start_ts,voting_end_ts,total_votes,status)
        #             VALUES (?, ? ,? ,? ,? ,? ,? )''', (
        #     dao_pid, callparams['function_called'], json.dumps(callparams['params']), callparams['voting_start_ts'],
        #     callparams['voting_end_ts'], 10, 0))
        transaction_creator = TransactionCreator()
        txtype1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)
        return [txtype1]

    def vote_on_proposal(self, callparamsip, repo: FetchRepository):
        trxn = []
        transaction_creator = TransactionCreator()
        callparams = input_to_dict(callparamsip)
        # ToDO Voting to be saved in
        callparams['address'] = self.address
        # vote_on_proposal(cur, callparams)
        if self.dao_type == 2 or self.valid_member(repo, callparams):

            member_pid = self.__get_pid_from_wallet_using_repo(
                repo, callparams['function_caller'][0]['wallet_address'])
            proposal_id = callparams['proposal_id']
            qparam = {"proposal_id": proposal_id}
            voter_db_data = repo.select_Query(
                "voter_data,yes_votes,no_votes,abstain_votes,total_votes,function_called").add_table_name(
                "proposal_data").where_clause("proposal_id", proposal_id, 1).execute_query_single_result(qparam)
            # voter_db_data = cur.execute('''Select voter_data as "voter_data",yes_votes as "yes_votes",no_votes as "no_votes",abstain_votes as "abstain_votes",total_votes as "total_votes",function_called as "function_called"  from proposal_data where proposal_id = ?''', (proposal_id,))
            # voter_db_data=voter_db_data.fetchone()

            # Initializing  the voter_db_data variable
            if (voter_db_data[0] is None):
                voter_db_data = ['{}', 0, 0, 0,
                                 voter_db_data[4], voter_db_data[5]]
            voter_data = input_to_dict(json.loads(voter_db_data[0]))
            yes_votes = voter_db_data[1]
            no_votes = voter_db_data[2]
            abstain_votes = voter_db_data[3]
            total_votes = voter_db_data[4]
            function_called = voter_db_data[5]
            weight = 1
            if (self.dao_type == 2):
                paramtopass = {}
                paramtopass['dao_id'] = self.address
                paramtopass['person_id'] = member_pid
                weight = self.get_token_lock_amount(
                    json.dumps(callparamsip), repo)
            if (self.duplicate_check(voter_db_data[0], member_pid)):

                if (callparams['vote'] == -1):
                    no_votes = no_votes + weight
                elif (callparams['vote'] == 1):
                    yes_votes = yes_votes + weight
                else:
                    abstain_votes = abstain_votes + weight

                voter_data[member_pid] = {
                    "vote": callparams['vote'], "weight": weight}
                sc_state_proposal1_data = {
                    "operation": "update",
                    "table_name": "proposal_data",
                    "sc_address": self.address,
                    "data": {
                        "voter_data": json.dumps(voter_data),
                        "yes_votes": yes_votes,
                        "no_votes": no_votes,
                        "abstain_votes": abstain_votes,

                    },
                    "unique_column": "proposal_id",
                    "unique_value": proposal_id
                }
                trxn.append(transaction_creator.transaction_type_8(
                    sc_state_proposal1_data))
                # cur.execute(f'''update proposal_data set voter_data=?,yes_votes=?,no_votes=?,abstain_votes=?  where proposal_id = ?''',(json.dumps(voter_data),yes_votes,no_votes,abstain_votes,proposal_id))
            else:
                return []

            # get voting scheme params from dao params
            cspecs = input_to_dict(self.contractparams['contractspecs'])
            voting_schemes = cspecs['voting_schemes']
            voting_scheme_params = None
            voting_scheme_selected = None
            for method in voting_schemes:
                if (method['function'] == function_called):
                    voting_scheme_params = method['params']
                    voting_scheme_selected = method['voting_scheme']

            # get total votes, current yes and no votes from proposal
            voting_specs = {
                'voting_scheme_params': voting_scheme_params,
                'current_yes_votes': yes_votes,
                'current_no_votes': no_votes,
                'total_votes': total_votes,
                'cspecs': cspecs,
                'sender': callparams['function_caller'][0]['wallet_address']
            }

            funct = getattr(Utils, voting_scheme_selected)
            voting_result = funct(voting_specs)
            # check if any condition is met
            # if yes (-1 or 1)
            # update the db
            # execute the function

            if (voting_result == 1):
                sc_state_proposal1_data = {
                    "operation": "update",
                    "table_name": "proposal_data",
                    "sc_address": self.address,
                    "data": {
                        "status": "accepted",
                    },
                    "unique_column": "proposal_id",
                    "unique_value": proposal_id
                }
                # cur.execute('''update proposal_data set status = ? where proposal_id= ?''',("accepted",callparamsip['proposal_id']))
                trxn.append(transaction_creator.transaction_type_8(
                    sc_state_proposal1_data))
                trxn.extend(self.execute(callparamsip, repo))
            if (voting_result == -1):
                sc_state_proposal1_data = {
                    "operation": "update",
                    "table_name": "proposal_data",
                    "sc_address": self.address,
                    "data": {
                        "status": "rejected",
                    },
                    "unique_column": "proposal_id",
                    "unique_value": proposal_id
                }
                trxn.append(transaction_creator.transaction_type_8(
                    sc_state_proposal1_data))
                return trxn
                # cur.execute('''update proposal_data set status = ? where proposal_id= ?''',("rejected",callparamsip['proposal_id']))

        return trxn

    def execute(self, callparamsip, repo: FetchRepository):
        # proposal ( funct , paramsip) - votes status
        # Getting proposal Data
        callparams = input_to_dict(callparamsip)
        # proposal = cur.execute('''select function_called,params from proposal_data where  proposal_id=?''',
        #                        ("".join(str(callparams['proposal_id'])),))
        proposal = repo.select_Query("function_called,params").add_table_name("proposal_data").where_clause(
            "proposal_id", callparams['proposal_id'], 1).execute_query_single_result(
            {"proposal_id": callparams['proposal_id']})
        # proposal=proposal.fetchone()
        if (proposal is None):
            return False
        if self.check_status(callparamsip, repo):
            funct = getattr(self, proposal[0])
            return funct(proposal[1], repo)
        else:
            return []

    def add_member(self, callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
        qparam = {"dao_person_id": dao_pid,
                  "member_person_id": callparams['member_person_id']}
        is_dao_exist = repo.select_count().add_table_name("dao_membership").where_clause("dao_person_id",
                                                                                         qparam['dao_person_id'],
                                                                                         4).and_clause(
            "member_person_id", qparam['member_person_id'], 4).execute_query_single_result(qparam)
        # is_dao_exist = cur.execute(
        #     '''SELECT COUNT(*) FROM dao_membership WHERE dao_person_id LIKE ? AND member_person_id LIKE ?''',
        #     (dao_pid, callparams['member_person_id']))
        # is_dao_exist=is_dao_exist.fetchone()
        if (is_dao_exist[0] == 0):
            sc_state_proposal1_data = {
                "operation": "save",
                "table_name": "dao_membership",
                "sc_address": self.address,
                "data": {
                    "address": self.address,
                    "dao_person_id": dao_pid,
                    "member_person_id": callparams['member_person_id'],
                    "role": callparams.get("role", 0)
                }
            }
            transaction_creator = TransactionCreator()
            return [transaction_creator.transaction_type_8(sc_state_proposal1_data)]
        else:
            return []

    def delete_member(self, callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
        # Sql code to update Membership table
        sc_state_proposal1_data = {
            "operation": "delete",
            "table_name": "dao_membership",
            "sc_address": self.address,
            "unique_column": "member_person_id",
            "unique_value": callparams['member_person_id']
        }
        transaction_creator = TransactionCreator()
        return transaction_creator.transaction_type_8(sc_state_proposal1_data)
        # cur.execute('''DELETE FROM dao_membership
        #             WHERE dao_person_id= ?
        #             AND member_person_id= ? ''', (dao_pid, callparams['member_person_id']))

    def check_status(self, callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        return True

    def valid_member(self, repo: FetchRepository, callparamsip):
        callparams = input_to_dict(callparamsip)
        member_pid = self.__get_pid_from_wallet_using_repo(
            repo, callparams['function_caller'][0]['wallet_address'])
        # member_pid="".join(get_pid_from_wallet(cur,callparams['function_caller'][0]['wallet_address']))
        # proposal = cur.execute('''Select count(*) from dao_membership where member_person_id like ?''', [member_pid])
        qparam = {"member_person_id": member_pid}
        proposal = repo.select_count().add_table_name("dao_membership").where_clause("member_person_id", member_pid,
                                                                                     4).execute_query_single_result(
            qparam)
        if (proposal[0] == 0):
            return False
        return True

    def duplicate_check(self, voter_data, member_pid):
        voter_data = input_to_dict(json.loads(voter_data))
        for voter in voter_data.keys():
            if (voter == member_pid):
                return False
        return True

    '''Token based methods'''

    # Token unique to DAO created via below method hence in template
    def issue_token(self, callparamsip, repo: FetchRepository):
        '''
        TODO
        params : walletId , txnHash, amount
        function : check txn validity and issue dao tokens to that pid
        '''
        transacation_creator = TransactionCreator()
        trxn = []
        # call params
        callparams = input_to_dict(callparamsip)
        # Hash of Txn
        # transferTxn = callparams['transferTxn']

        recipient_address = callparams['recipient_address']
        amount = callparams['amount']
        # Stable Coin transfer from user to DAO
        # Value Code here $$$$$$
        # transfer_tokens_and_update_balances(
        #     cur, recipient_address, self.address, 'NWRL', amount)
        # issue tokens
        # dao_data=cur.execute(f'''Select dao_name as dao_name from dao_main where dao_sc_address=?''',[self.address])
        # dao_data=dao_data.fetchone()
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        token_name = cspecs['token_name']
        token_code = cspecs['token_code']
        exchange_token_code = cspecs['exchange_token_code']
        exchange_rate = cspecs['exchange_rate']
        value = callparams['value']

        required_value = {
            "token_code": exchange_token_code,
            "amount": value[0]["amount"]
        }

        if not required_value in value:
            raise Exception("Value sent is invalid. Provide correct tokens")

        amount_to_issue = math.floor(value[0]['amount'] / exchange_rate)
        tokendata = {
            "tokenname": token_name,
            "tokencode": token_code,
            "tokentype": '1',
            "tokenattributes": {},
            "first_owner": recipient_address,
            "custodian": self.address,
            "legaldochash": '',
            "amount_created": amount_to_issue,
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
        transacation_creator = TransactionCreator()
        trxn.append(transacation_creator.transaction_type_two(tokendata))
        return trxn

    def get_token_lock_amount(self, callparamsip, repo: FetchRepository):
        '''
        TODO
        params : pid , daoId, proposal_id
        function : check if any balance, add this proposal for that token status entry with current balance
        '''

        callparams = input_to_dict(callparamsip)
        dao_id = callparams['address']
        person_id = self.__get_pid_from_wallet_using_repo(
            repo, callparams['function_caller'][0]['wallet_address'])
        lock_data = repo.select_Query("amount_locked").add_table_name("DAO_TOKEN_LOCK").where_clause("person_id",
                                                                                                     person_id,
                                                                                                     1).and_clause(
            "dao_id", dao_id, 1).execute_query_single_result({"person_id": person_id, "dao_id": dao_id})
        # lock_data=cur.execute(f'''Select amount_locked from DAO_TOKEN_LOCK where person_id=? and dao_id=?''',[person_id,dao_id]).fetchone()
        return lock_data[0]
        # fetch current token value locked

    def set_price(self, cur, callapramsip):
        # To set the price at which token to be issued
        pass

    def lock_tokens(self, callparamsip, repo: FetchRepository):
        '''
        TODO
        params : person_pid, dao_id, amount, txnHash (of transfer to dao)
        function : add a new row with pid and amount++
        '''
        transaction_creator = TransactionCreator()
        trxn = []
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)
        dao_id = self.address
        person_id = callparams['person_id']
        value = callparams['value']
        token_code = cspecs['token_code']
        amount = value[0]['amount']
        required_value = {
            "token_code": token_code,
            "amount": amount
        }

        if not required_value in value:
            raise Exception(
                "Value sent is invalid. Can only lock dao specific tokens")

        lock_data = repo.select_Query("dao_id,person_id,amount_locked").add_table_name("DAO_TOKEN_LOCK").where_clause(
            "person_id", person_id, 1).and_clause("dao_id", dao_id, 1).execute_query_single_result(
            {"person_id": person_id, "dao_id": dao_id})
        if lock_data is None:
            sc_state_proposal1_data = {
                "operation": "save",
                "table_name": "DAO_TOKEN_LOCK",
                "sc_address": self.address,
                "data": {
                    "address": self.address,
                    "dao_id": dao_id,
                    "person_id": person_id,
                    "amount_locked": amount,
                    "wallet_address": callparams['function_caller'][0]['wallet_address']
                }
            }
            trxn.append(transaction_creator.transaction_type_8(
                sc_state_proposal1_data))
            # cur.execute(
            #     f'''Insert into DAO_TOKEN_LOCK (dao_id,person_id,amount_locked,wallet_address) values (?,?,?,?)''',
            #     (dao_id,person_id,amount,callparams['wallet_address']))
        else:
            amount = amount + lock_data[2]
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "DAO_TOKEN_LOCK",
                "sc_address": self.address,
                "data": {
                    "amount_locked": amount
                },
                "unique_column": "person_id",
                "unique_value": person_id
            }
            trxn.append(transaction_creator.transaction_type_8(
                sc_state_proposal1_data))
        return trxn

    def initialize_membership(self, callparamsip, repo: FetchRepository):
        trxn = []
        dao_params = repo.select_Query('founder_personid').add_table_name('dao_main').where_clause(
            'dao_sc_address', self.address, 1).execute_query_single_result({'dao_sc_address': self.address})
        if dao_params is None:
            return []
        for i in json.loads(dao_params[0]):
            pid = self.__get_pid_from_wallet_using_repo(repo, i)
            callparams = input_to_dict(callparamsip)
            dao_pid = self.__get_pid_from_wallet_using_repo(repo, self.address)
            qparam = {"dao_person_id": dao_pid, "member_person_id": pid}
            is_dao_exist = repo.select_count().add_table_name("dao_membership").where_clause("dao_person_id",
                                                                                             qparam['dao_person_id'],
                                                                                             4).and_clause(
                "member_person_id", qparam['member_person_id'], 4).execute_query_single_result(qparam)
            # is_dao_exist = cur.execute(
            #     '''SELECT COUNT(*) FROM dao_membership WHERE dao_person_id LIKE ? AND member_person_id LIKE ?''',
            #     (dao_pid, callparams['member_person_id']))
            # is_dao_exist=is_dao_exist.fetchone()
            if (is_dao_exist[0] == 0):
                sc_state_proposal1_data = {
                    "operation": "save",
                    "table_name": "dao_membership",
                    "sc_address": self.address,
                    "data": {
                        "address": self.address,
                        "dao_person_id": dao_pid,
                        "member_person_id": pid,
                    }
                }
                transaction_creator = TransactionCreator()
                trxn.append(transaction_creator.transaction_type_8(
                    sc_state_proposal1_data))
            else:
                return trxn
        return trxn

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
    def __get_pid_from_wallet_using_repo(self, repo: FetchRepository, address):
        if not address.startswith('ct'):
            spec = repo.select_Query('specific_data').add_table_name('wallets').where_clause('wallet_address', address,
                                                                                             1).execute_query_single_result(
                {'wallet_address': address})
            spec = input_to_dict(spec[0])
            if 'linked_wallet' in spec:
                address = spec['parentaddress']
        pid = repo.select_Query("person_id").add_table_name("person_wallet").where_clause("wallet_id", address,
                                                                                          1).execute_query_single_result(
            {"wallet_id": address})
        if pid is not None:
            return pid[0]
        return None
