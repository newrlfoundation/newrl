# class to stake token from user
import math

from .contract_master import ContractMaster
from ..clock.global_time import get_corrected_time_ms
from ..db.db_updater import *
from ..helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
import logging
from app.core.helpers.utils import get_last_block_hash

from app.config.nvalues import STAKE_COOLDOWN_MS


class NewrlStakeContract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, contractaddress=None):
        self.template = "NewrlStakeContract"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def stake_tokens(self, callparamsip, repo: FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        token_code = 'NWRL'
        token_amount = callparams['token_amount']
        required_value = {"token_code": token_code, "amount": token_amount}
        wallet_address = callparams['wallet_address']
        staker_wallet = callparams['function_caller'][0]['wallet_address']
        if callparams['token_amount'] < 0:
            self.logger.info("Amount should pe positive Integer.")
        pid = self.__get_pid_from_wallet_using_repo(repo, wallet_address)
        if pid is None:
            self.logger.info('PID not found for wallet %s', wallet_address)
            return []
        if required_value in callparams["value"]:
            count = repo.select_count().add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                    1).and_clause("address",self.address,1).execute_query_single_result(
                {"person_id": pid,"address": self.address})
            if count[0] == 0:
                sc_state_proposal1_data = {
                    "operation": "save",
                    "table_name": "stake_ledger",
                    "sc_address": self.address,
                    "data": {
                        "person_id": pid,
                        "amount": token_amount,
                        "time_updated": get_last_block_hash()["timestamp"],
                        "wallet_address": wallet_address,
                        "address": self.address,
                        "staker_wallet_address": json.dumps([{
                            staker_wallet: token_amount
                        }, ])
                    }
                }
                transaction_creator = TransactionCreator()
                txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                trxn.append(txtype1)
            else:
                count = repo.select_count().add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                        1).and_clause("address", self.address,1).execute_query_single_result(
                    {"person_id": pid, "wallet_address": wallet_address,"address": self.address})
                amount = repo.select_Query("amount,staker_wallet_address").add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                                 1).and_clause(
                    "wallet_address", wallet_address, 1).and_clause("address", self.address,1).execute_query_single_result(
                    {"person_id": pid, "wallet_address": wallet_address,"address":self.address})
                if count[0] == 1:
                    updated_value=False
                    staker_wallet_address_json=input_to_dict(amount[1])
                    for i in staker_wallet_address_json:
                        if staker_wallet in i.keys():
                            i[staker_wallet]=i[staker_wallet]+token_amount
                            updated_value=True
                            break
                    if not updated_value:
                        staker_wallet_address_json.append({staker_wallet:token_amount})

                    sc_state_proposal1_data = {
                        "operation": "update",
                        "table_name": "stake_ledger",
                        "sc_address": self.address,
                        "data": {
                            "amount": amount[0] + token_amount,
                            "time_updated": get_last_block_hash()["timestamp"],
                            "staker_wallet_address":json.dumps(staker_wallet_address_json)
                        },
                        "unique_column": "person_id",
                        "unique_value": pid,
                    }
                    transaction_creator = TransactionCreator()
                    txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                    trxn.append(txtype1)
                else:
                    self.logger.info("Initial Stake wallet does not match the signer wallet.")
        else:
            logger.error("Value provided isnt matching required value")
            raise Exception("Value provided isnt matching required value")
        return trxn

    def unstake_tokens(self, callparamsip, repo: FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        wallet_address = callparams.get("wallet_address",callparams['function_caller'][0]['wallet_address'])
        qparam = {"person_id": callparams['person_id'], "wallet_address": wallet_address,"address":self.address}
        data = repo.select_Query('time_updated,amount,staker_wallet_address').add_table_name('stake_ledger').where_clause('person_id',
                                                                                                    callparams[
                                                                                                        'person_id'],
                                                                                                    1).and_clause(
            "wallet_address", wallet_address, 1).and_clause("address", self.address,1).execute_query_single_result(qparam)
        staker_wallet_address=callparams['function_caller'][0]['wallet_address']
        
        partial_unstake = False
        if "token_amount" in callparams.keys():
            if callparams['token_amount'] < 0:
                self.logger.info("token amount should pe positive Integer.")
            partial_unstake = True

        amount_exist=0
        amount_to_unstake = 0
        if data is None:
            return trxn
        data_json=json.loads(data[2])
        for index, value in enumerate(data_json):
            if staker_wallet_address in value.keys():
                amount_exist=value[staker_wallet_address]
                if partial_unstake:
                    if amount_exist < callparams['token_amount']:
                        raise Exception("Requested partial unstake exceeds stake present")
                    amount_to_unstake = callparams['token_amount']
                    data_json[index][staker_wallet_address] = amount_exist - callparams['token_amount']
                else: 
                    data_json[index][staker_wallet_address] = 0
                    amount_to_unstake = amount_exist    
                break

        if get_last_block_hash()["timestamp"] >= (int(data[0]) + int(Configuration.config("STAKE_COOLDOWN_MS"))):
            transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": 'NWRL',
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": staker_wallet_address,
                "asset1_number": int(amount_to_unstake),
                "asset2_number": 0,
                "additional_data": {}
            }
            transaction_creator = TransactionCreator()
            trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "stake_ledger",
                "sc_address": self.address,
                "data": {
                    "amount": math.floor(data[1]-amount_to_unstake),
                    "time_updated": get_last_block_hash()["timestamp"],
                    "staker_wallet_address":json.dumps(data_json),
                },
                "unique_column": "person_id",
                "unique_value": callparams['person_id']
            }
            transaction_creator = TransactionCreator()
            txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
            trxn.append(txtype1)

        return trxn



    def __get_pid_from_wallet_using_repo(self, repo: FetchRepository, address):
        pid = repo.select_Query('person_id').add_table_name('person_wallet').where_clause('wallet_id', address,
                                                                                         1).execute_query_single_result(
            {'wallet_id': address})

        if pid:
            return pid[0]
        return None

