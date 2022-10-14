

import json
import math
from re import T
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from app.nvalues import STAKE_CT_ADDRESS, ZERO_ADDRESS
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
        # TODO check for self balance
        callparams = input_to_dict(callparamsip)
        token_code = cspecs['issuance_token_code']
        token_multiplier = cspecs['token_multiplier']
        value = callparams['value']
        wallet_address = callparams['wallet_address']
        amount_to_issue = value[0]['amount']
        amount_to_stake = amount_to_issue * token_multiplier
        staker_wallet = callparams['function_caller'][0]['wallet_address']

        required_value = {
            "token_code": token_code,
            "amount": amount_to_issue
        }
        pid = self.__get_pid_from_wallet_using_repo(repo, wallet_address)

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
                        "time_updated": get_corrected_time_ms(),
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
                            "time_updated": get_corrected_time_ms(),
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
        # TODO check for self balance
        callparams = input_to_dict(callparamsip)
        issuance_token_code = cspecs['issuance_token_code']
        token_multiplier = cspecs['token_multiplier']
        wallet_address = callparams['wallet_address']
        person_id = callparams['person_id']
        og_unstake_amount = callparams['og_unstake_amount']
        newrl_unstake_amount = og_unstake_amount * token_multiplier

        if not self.__check_if_slashed(wallet_address,person_id,og_unstake_amount, token_multiplier,repo):
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
        for index, value in enumerate(data_json):
            if staker_wallet_address in value.keys():
                amount_update = value[staker_wallet_address]
                if amount_update > og_unstake_amount or amount_update < og_unstake_amount:
                    raise Exception("Cant unstake partial or excess amount")
                data_json[index][staker_wallet_address] = 0
                break

        # if get_corrected_time_ms() >= (int(data[0]) + STAKE_COOLDOWN_MS):
        if True:
            transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": 'NWRL',
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": staker_wallet_address,
                "asset1_number": int(amount_update),
                "asset2_number": 0,
                "additional_data": {}
            }
            transaction_creator = TransactionCreator()
            child_transactions.append(transaction_creator.transaction_type_5(
                transfer_proposal_data))
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "stake_ledger",
                "sc_address": self.address,
                "data": {
                    "amount": math.floor(data[1]-amount_update),
                    "time_updated": get_corrected_time_ms(),
                    "staker_wallet_address": json.dumps(data_json),
                },
                "unique_column": "person_id",
                "unique_value": callparams['person_id']
            }
            transaction_creator = TransactionCreator()
            txtype1 = transaction_creator.transaction_type_8(
                sc_state_proposal1_data)
            child_transactions.append(txtype1)

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

        # add type 5 transaction to transfer back og
        '''txn type 5 (one way transfer)'''
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": issuance_token_code,
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": wallet_address,
            "asset1_number": og_unstake_amount,
            "asset2_number": 0,
            "additional_data": {}       
        }
        transfer_proposal = transaction_creator.transaction_type_5(
            transfer_proposal_data)
        child_transactions.append(transfer_proposal)
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
                "transfer_type": 1,
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
            
