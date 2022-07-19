# class to stake token from user
from .contract_master import ContractMaster
from ..clock.global_time import get_corrected_time_ms
from ..db_updater import *
from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator
import logging

from ...nvalues import STAKE_COOLDOWN_MS


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
        wallet_address = callparams['function_caller'][0]['wallet_address']
        if callparams['token_amount'] < 0:
            self.logger.info("Amount should pe positive Integer.")
        pid = self.__get_pid_from_wallet_using_repo(repo, wallet_address)
        if required_value in callparams["value"]:
            count = repo.select_count().add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                             1).execute_query_single_result(
                {"person_id": pid})
            if count[0] == 0:
                sc_state_proposal1_data = {
                    "operation": "save",
                    "table_name": "stake_ledger",
                    "sc_address": self.address,
                    "data": {
                        "person_id": pid,
                        "amount": token_amount,
                        "time_updated": get_corrected_time_ms(),
                        "wallet_address": wallet_address,
                        "address":self.address
                    }
                }
                transaction_creator = TransactionCreator()
                txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                trxn.append(txtype1)
            else:
                count = repo.select_count().add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                 1).and_clause("wallet_address",
                                                                                               wallet_address,
                                                                                               1).execute_query_single_result(
                    {"person_id": pid, "wallet_address": wallet_address})
                amount = repo.select_Query("amount").add_table_name("stake_ledger").where_clause("person_id", pid,
                                                                                          1).and_clause(
                    "wallet_address", wallet_address, 1).execute_query_single_result(
                    {"person_id": pid, "wallet_address": wallet_address})
                if count[0] == 1:
                    sc_state_proposal1_data = {
                        "operation": "update",
                        "table_name": "stake_ledger",
                        "sc_address": self.address,
                        "data": {
                            "amount": amount[0] + token_amount,
                            "time_updated": get_corrected_time_ms()
                        },
                        "unique_column": "person_id",
                        "unique_value":pid,
                    }
                    transaction_creator = TransactionCreator()
                    txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                    trxn.append(txtype1)
                else:
                    self.logger.info("Initial Stake wallet does not match the signer wallet.")
        return trxn


    def unstake_tokens(self, callparamsip, repo: FetchRepository):
        trxn=[]
        callparams=input_to_dict(callparamsip)
        wallet_address = callparams['function_caller'][0]['wallet_address']
        qparam={"person_id":callparams['person_id'],"wallet_address":wallet_address}
        data=repo.select_Query('time_updated,amount').add_table_name('stake_ledger').where_clause('person_id',callparams['person_id'],1).and_clause("wallet_address",wallet_address,1).execute_query_single_result(qparam)
        if data is None:
            return trxn
        if get_corrected_time_ms()>=(int(data[0])+STAKE_COOLDOWN_MS):
            transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": 'NWRL',
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": wallet_address,
                "asset1_number": float(data[1]),
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
                    "amount": 0,
                    "time_updated": get_corrected_time_ms()
                },
                   "unique_column": "person_id",
                        "unique_value":callparams['person_id']
            }
            transaction_creator = TransactionCreator()
            txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
            trxn.append(txtype1)
        else:
            self.logger.info("can not unstake before cooldown time.")
        return trxn



    def __get_pid_from_wallet_using_repo(self, repo: FetchRepository, address):
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

#
