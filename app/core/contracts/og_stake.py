

import json
import math
from re import T
from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
from app.core.helpers.utils import get_last_block_hash
from app.config.nvalues import STAKE_COOLDOWN_MS, STAKE_CT_ADDRESS, ZERO_ADDRESS
from app.config.Configuration import Configuration
from .contract_master import ContractMaster
from ..clock.global_time import get_corrected_time_ms

class og_stake(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "og_stake"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    
    #todo add contract address in fetch

    def stake(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)
        token_code = cspecs['issuance_token_code']
        token_stake_multiplier = cspecs['token_stake_multiplier']
        value = callparams['value']
        wallet_address = callparams['wallet_address']
        amount_to_issue = cspecs['stake_allowed']
        amount_to_stake = amount_to_issue * token_stake_multiplier
        staker_wallet = callparams['function_caller'][0]['wallet_address']
        pid = self.__get_pid_from_wallet_using_repo(repo, wallet_address)

        if self.__check_if_already_staked(pid,repo):
            raise Exception("Staking alredy present for this address")

        contract_balance = self._fetch_token_balance("NWRL",self.address,repo)
        if contract_balance < amount_to_stake:
            raise Exception("Insufficient balance in the contract")

        required_value = {
            "token_code": token_code,
            "amount": amount_to_issue
        }

        child_transactions = []    

        if required_value in value:
            count = repo.select_count().add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                    1).and_clause("address", self.address,1).execute_query_single_result(
                {"person_id": pid, "address": self.address})
            if count[0] == 0:
                sc_state_proposal1_data = {
                    "operation": "save",
                    "table_name": "stake_ledger",
                    "sc_address": self.address,
                    "data": {
                        "person_id": pid,
                        "amount": amount_to_issue,
                        "time_updated": get_last_block_hash()["timestamp"],
                        "wallet_address": wallet_address,
                        "address": self.address,
                        "staker_wallet_address": json.dumps([{
                            staker_wallet: amount_to_issue
                        }, ])
                    }
                }
                transaction_creator = TransactionCreator()
                txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                child_transactions.append(txtype1)
            else:
                count = repo.select_count().add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                        1).and_clause("address", self.address,1).execute_query_single_result(
                    {"person_id": pid, "wallet_address": wallet_address, "address": self.address})
                amount = repo.select_Query("amount,staker_wallet_address").add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                                 1).and_clause(
                    "wallet_address", wallet_address, 1).and_clause("address", self.address,1).execute_query_single_result(
                    {"person_id": pid, "wallet_address": wallet_address,"address":self.address})
                if count[0] == 1:
                    updated_value=False
                    staker_wallet_address_json=input_to_dict(amount[1])
                    for i in staker_wallet_address_json:
                        if staker_wallet in i.keys():
                            i[staker_wallet]=i[staker_wallet]+amount_to_issue
                            updated_value=True
                            break
                    if not updated_value:
                        staker_wallet_address_json.append({staker_wallet:amount_to_issue})

                    sc_state_proposal1_data = {
                        "operation": "update",
                        "table_name": "stake_ledger",
                        "sc_address": self.address,
                        "data": {
                            "amount": amount[0] + amount_to_issue,
                            "time_updated": get_last_block_hash()["timestamp"],
                            "staker_wallet_address":json.dumps(staker_wallet_address_json)
                        },
                        "unique_column": "person_id",
                        "unique_value": pid,
                    }
                    transaction_creator = TransactionCreator()
                    txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                    child_transactions.append(txtype1)
                else:
                    self.logger.info("Initial Stake wallet does not match the signer wallet.")
 
            transaction_creator = TransactionCreator()
            params = {
                "token_amount":amount_to_stake,
                "wallet_address": wallet_address,
                "value": [
                    {
                        "token_code": "NWRL",
                        "amount": amount_to_stake,
                    }
                ]
            }
            txspecdata = {
                "address": STAKE_CT_ADDRESS,
                "function": 'stake_tokens',
                "signers": [self.address],
                "params": params,
            }
            sc_transaction = transaction_creator.transaction_type_3(txspecdata)
            child_transactions.append(sc_transaction)
            return child_transactions

    def unstake(self, callparamsip, repo: FetchRepository):
        
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        og_unstake_token_code = cspecs['og_unstake_token_code']
        og_unstake_token_name = cspecs['og_unstake_token_name']

        
        token_stake_multiplier = cspecs['token_stake_multiplier']
        wallet_address = callparams['wallet_address']
        person_id = callparams['person_id']
        og_unstake_amount = cspecs['stake_allowed']
        newrl_unstake_amount = og_unstake_amount * token_stake_multiplier

        if not self.__check_if_slashed(wallet_address, person_id, og_unstake_amount, token_stake_multiplier, repo):
            raise Exception("Newrl stake has been slashed, cant withdraw og for now")
        child_transactions = []

        qparam = {"person_id": callparams['person_id'],
                  "wallet_address": wallet_address, "address": self.address}
        data = repo.select_Query('time_updated,amount,staker_wallet_address').add_table_name('stake_ledger').where_clause('person_id',
                                                                                                    callparams[
                                                                                                        'person_id'],
                                                                                                    1).and_clause(
            "wallet_address", wallet_address, 1).and_clause("address", self.address,1).execute_query_single_result(qparam)
      
        staker_wallet_address = callparams['function_caller'][0]['wallet_address']
        amount_update = 0
        if data is None:
            raise Exception("No existing og stake entry for this data")
        data_json = json.loads(data[2])
        staker_present = False
        for index, value in enumerate(data_json):
            if staker_wallet_address in value.keys():
                amount_update = value[staker_wallet_address]
                if amount_update > og_unstake_amount or amount_update < og_unstake_amount:
                    raise Exception("Cant unstake partial or excess amount")
                data_json[index][staker_wallet_address] = 0
                staker_present = True
                break

        if not staker_present:
            raise Exception("Staker / Signer is not present in staker list for this wallet, cant unstake")        
        if get_last_block_hash()["timestamp"] >= (int(data[0]) + int(Configuration.config("STAKE_COOLDOWN_MS"))):
        #call sc newrl txn
            transaction_creator = TransactionCreator()
            params = {
                "token_amount": newrl_unstake_amount,
                "wallet_address": wallet_address,
                "person_id": person_id
            }
            txspecdata = {
                "address": STAKE_CT_ADDRESS,
                "function": 'unstake_tokens',
                "signers": [self.address],
                "params": params,
                "function_caller": self.address
            }
            sc_transaction = transaction_creator.transaction_type_3(txspecdata)
            child_transactions.append(sc_transaction)

            # type 2 to issue og_unstake token
            transaction_creator = TransactionCreator()
            tokendata = {
                    "tokenname": og_unstake_token_name,
                    "tokencode": og_unstake_token_code,
                    "tokentype": '1',
                    "tokenattributes": {},
                    "first_owner": staker_wallet_address,
                    "custodian": self.address,
                    "legaldochash": '',
                    "amount_created": 1,
                    "value_created": '',
                    "disallowed": {},
                    "sc_flag": True,
                }
            og_unstake = transaction_creator.transaction_type_two(tokendata)
            child_transactions.append(og_unstake)

            # type 8 to change stake ledger data
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "stake_ledger",
                "sc_address": self.address,
                "data": {
                    "amount": math.floor(data[1]-amount_update),
                    "time_updated": get_last_block_hash()["timestamp"],
                    "staker_wallet_address": json.dumps(data_json),
                },
                "unique_column": "person_id",
                "unique_value": callparams['person_id']
            }
            transaction_creator = TransactionCreator()
            txtype1 = transaction_creator.transaction_type_8(
                sc_state_proposal1_data)
            child_transactions.append(txtype1)
        else:
            raise Exception("Stake cooldown period not yet finished")    
        return child_transactions

    def unstake_master_former(self, callparamsip, repo: FetchRepository):

        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        og_unstake_token_code = cspecs['og_unstake_token_code']
        og_unstake_token_name = cspecs['og_unstake_token_name']

        token_stake_multiplier = cspecs['token_stake_multiplier']
        wallet_address = callparams['wallet_address']
        person_id = callparams['person_id']
        og_unstake_amount = cspecs['stake_allowed']
        newrl_unstake_amount = og_unstake_amount * token_stake_multiplier

        if not self.__check_if_slashed(wallet_address, person_id, og_unstake_amount, token_stake_multiplier, repo):
            raise Exception(
                "Newrl stake has been slashed, cant withdraw og for now")
        child_transactions = []

        qparam = {"person_id": callparams['person_id'],
                  "wallet_address": wallet_address, "address": self.address}
        data = repo.select_Query('time_updated,amount,staker_wallet_address').add_table_name('stake_ledger').where_clause('person_id',
                                                                                                                          callparams[
                                                                                                                              'person_id'],
                                                                                                                          1).and_clause(
            "wallet_address", wallet_address, 1).and_clause("address", self.address, 1).execute_query_single_result(qparam)

        staker_wallet_address = callparams['staker_wallet_address']
        amount_update = 0
        if data is None:
            raise Exception("No existing og stake entry for this data")
        data_json = json.loads(data[2])
        for index, value in enumerate(data_json):
            if staker_wallet_address in value.keys():
                amount_update = value[staker_wallet_address]
                if amount_update != og_unstake_amount:
                    raise Exception("Cant unstake partial or excess amount")
                data_json[index][staker_wallet_address] = 0
                break

        if get_last_block_hash()["timestamp"] >= (int(data[0]) + int(Configuration.config("STAKE_COOLDOWN_MS"))):
            #call sc newrl txn
            transaction_creator = TransactionCreator()
            params = {
                "token_amount": newrl_unstake_amount,
                "wallet_address": wallet_address,
                "person_id": person_id
            }
            txspecdata = {
                "address": STAKE_CT_ADDRESS,
                "function": 'unstake_tokens',
                "signers": [self.address],
                "params": params,
                "function_caller": self.address
            }
            sc_transaction = transaction_creator.transaction_type_3(txspecdata)
            child_transactions.append(sc_transaction)

            # type 2 to issue og_unstake token
            transaction_creator = TransactionCreator()
            tokendata = {
                "tokenname": og_unstake_token_name,
                "tokencode": og_unstake_token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": staker_wallet_address,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": 1,
                "value_created": '',
                "disallowed": {},
                "sc_flag": True,
            }
            og_unstake = transaction_creator.transaction_type_two(tokendata)
            child_transactions.append(og_unstake)

            # type 8 to change stake ledger data
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "stake_ledger",
                "sc_address": self.address,
                "data": {
                    "amount": math.floor(data[1]-amount_update),
                    "time_updated": get_last_block_hash()["timestamp"],
                    "staker_wallet_address": json.dumps(data_json),
                },
                "unique_column": "person_id",
                "unique_value": callparams['person_id']
            }
            transaction_creator = TransactionCreator()
            txtype1 = transaction_creator.transaction_type_8(
                sc_state_proposal1_data)
            child_transactions.append(txtype1)
        else:
            raise Exception("Stake cooldown period not yet finished")
        return child_transactions

    def unstake_master(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        partial_newrl_unstake_amount = callparams['partial_newrl_unstake_amount']
        og_unstake_token_code = cspecs['og_unstake_token_code']
        og_unstake_token_name = cspecs['og_unstake_token_name']

        token_stake_multiplier = cspecs['token_stake_multiplier']
        wallet_address = callparams['wallet_address']
        person_id = callparams['person_id']
        og_unstake_amount = cspecs['stake_allowed']
        newrl_unstake_amount = og_unstake_amount * token_stake_multiplier

        if partial_newrl_unstake_amount < 0:
                self.logger.info("token amount should pe positive Integer.")

        #TODO add diff validation
        # if not self.__check_if_slashed(wallet_address, person_id, og_unstake_amount, token_stake_multiplier, repo):
        #     raise Exception(
        #         "Newrl stake has been slashed, cant withdraw og for now")

        child_transactions = []

        #og stake query
        qparam = {"person_id": callparams['person_id'],
                  "wallet_address": wallet_address, "address": self.address}
        data = repo.select_Query('time_updated,amount,staker_wallet_address').add_table_name('stake_ledger').where_clause('person_id',
                                                                                                                          callparams[
                                                                                                                              'person_id'],
                                                                                                                          1).and_clause(
            "wallet_address", wallet_address, 1).and_clause("address", self.address, 1).execute_query_single_result(qparam)

        staker_wallet_address = wallet_address
        amount_update = 0
        existing_og_stake = 0

        #newrl stake query
        qparam = {"person_id": callparams['person_id'],
                  "wallet_address": wallet_address, "address": STAKE_CT_ADDRESS}
        newrl_stake_data = repo.select_Query('amount').add_table_name('stake_ledger').where_clause('person_id',
                                                                                                                          callparams[
                                                                                                                              'person_id'],
                                                                                                                          1).and_clause(
            "wallet_address", wallet_address, 1).and_clause("address", STAKE_CT_ADDRESS, 1).execute_query_single_result(qparam)
        newrl_updated_stake = newrl_stake_data[0]-partial_newrl_unstake_amount
        is_newrl_stake_depleted = newrl_updated_stake < 1
        if data is None:
            raise Exception("No existing og stake entry for this data")
        data_json = json.loads(data[2])
        for index, value in enumerate(data_json):
            if staker_wallet_address in value.keys():
                existing_og_stake = value[staker_wallet_address]
                if not existing_og_stake > 0:
                    raise Exception("Cant unstake via OG Unstake as current OG STAKE is 0")
                if is_newrl_stake_depleted:
                    amount_update = value[staker_wallet_address]    
                    data_json[index][staker_wallet_address] = 0
                break

        if get_last_block_hash()["timestamp"] >= (int(data[0]) + int(Configuration.config("STAKE_COOLDOWN_MS"))):
            #call sc newrl txn
            transaction_creator = TransactionCreator()
            params = {
                "token_amount": partial_newrl_unstake_amount,
                "wallet_address": wallet_address,
                "person_id": person_id
            }
            txspecdata = {
                "address": STAKE_CT_ADDRESS,
                "function": 'unstake_tokens',
                "signers": [self.address],
                "params": params,
                "function_caller": self.address
            }
            sc_transaction = transaction_creator.transaction_type_3(txspecdata)
            child_transactions.append(sc_transaction)


            #if new stake amount is 0, then unstake og and update the stake ledger data.
            if is_newrl_stake_depleted:
            # type 2 to issue og_unstake token
                transaction_creator = TransactionCreator()
                tokendata = {
                    "tokenname": og_unstake_token_name,
                    "tokencode": og_unstake_token_code,
                    "tokentype": '1',
                    "tokenattributes": {},
                    "first_owner": staker_wallet_address,
                    "custodian": self.address,
                    "legaldochash": '',
                    "amount_created": 1,
                    "value_created": '',
                    "disallowed": {},
                    "sc_flag": True,
                }
                og_unstake = transaction_creator.transaction_type_two(tokendata)
                child_transactions.append(og_unstake)

                # type 8 to change stake ledger data
                sc_state_proposal1_data = {
                    "operation": "update",
                    "table_name": "stake_ledger",
                    "sc_address": self.address,
                    "data": {
                        "amount": math.floor(data[1]-amount_update),
                        "time_updated": get_last_block_hash()["timestamp"],
                        "staker_wallet_address": json.dumps(data_json),
                    },
                    "unique_column": "person_id",
                    "unique_value": callparams['person_id']
                }
                transaction_creator = TransactionCreator()
                txtype1 = transaction_creator.transaction_type_8(
                    sc_state_proposal1_data)
                child_transactions.append(txtype1)
        else:
            raise Exception("Stake cooldown period not yet finished")
        return child_transactions


    def remove(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        withdraw_address = cspecs['withdraw_address']
        amount = callparams['amount']
        issuer = cspecs['issuer']

        function_caller = callparams['function_caller'][0]['wallet_address']

        if issuer != function_caller:
            raise Exception("Caller is not authorized")

        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
                "asset1_code": "NWRL",
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": withdraw_address,
                "asset1_number": amount,
                "asset2_number": 0,
                "additional_data": {}
            }
        transfer_proposal = transaction_creator.transaction_type_5(
                transfer_proposal_data)

        return [transfer_proposal]

    def initialize_tokens(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        og_unstake_token_code = cspecs['og_unstake_token_code']
        og_unstake_token_name = cspecs['og_unstake_token_name']

        child_transactions = []
        # type 2 to issue og_unstake token
        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": og_unstake_token_name,
            "tokencode": og_unstake_token_code,
            "tokentype": '1',
            "tokenattributes": {},
            "first_owner": self.address,
            "custodian": self.address,
            "legaldochash": '',
            "amount_created": 1,
            "value_created": '',
            "disallowed": {},
            "sc_flag": True,
        }
        og_unstake = transaction_creator.transaction_type_two(tokendata)
        child_transactions.append(og_unstake)
        return child_transactions

    def __get_pid_from_wallet_using_repo(self, repo: FetchRepository, address):
        pid = repo.select_Query('person_id').add_table_name('person_wallet').where_clause('wallet_id', address,
                                                                                          1).execute_query_single_result(
            {'wallet_id': address})

        if pid:
            return pid[0]
        return None

    def __check_if_slashed(self,wallet_address,person_id,og_unstake_amount, token_multiplier, repo: FetchRepository):
        qparam = {"person_id": person_id,
                  "wallet_address": wallet_address, "address": STAKE_CT_ADDRESS}
        data = repo.select_Query('time_updated,amount,staker_wallet_address').add_table_name('stake_ledger').where_clause('person_id',
                                                                                                    person_id,
                                                                                                    1).and_clause(
            "wallet_address", wallet_address, 1).and_clause("address", STAKE_CT_ADDRESS,1).execute_query_single_result(qparam)
      
        staker_wallet_address = self.address
        amount_update = 0

        if data is None:
            raise Exception("No existing newrl stake entry for this data")
        data_json = json.loads(data[2])
        for index, value in enumerate(data_json):
            if staker_wallet_address in value.keys():
                amount_update = value[staker_wallet_address]
                break
        return amount_update >= og_unstake_amount*token_multiplier
            
    def _fetch_token_balance(self, token_code, address, repo):
        balance = repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address", address, 1).and_clause(
            "tokencode", token_code, 1).execute_query_single_result({"wallet_address": address, "tokencode": token_code})
        if balance == None:
            return 0
        return balance[0]

    def __check_if_already_staked(self,person_id,repo):
        stakers = repo.select_Query().add_table_name("stake_ledger").where_clause("person_id", person_id,1).and_clause("address", self.address,1).execute_query_single_result({"person_id": person_id, "address": self.address})
        if stakers == None:
            return False
        return stakers[0]
        
