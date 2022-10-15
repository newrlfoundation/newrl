# class to stake token from user
import math
import hashlib
from .contract_master import ContractMaster
from ..clock.global_time import get_corrected_time_ms
from ..db_updater import *
from ..helpers.CustomExceptions import ContractValidationError
from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator
import logging

from ...nvalues import STAKE_COOLDOWN_MS


class PledgingContract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, contractaddress=None):
        self.template = "PledgingContract"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def pledge_tokens(self, callparamsip, repo: FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams)
        custodian_address = cspecs['custodian_address']
        tokens = callparams['tokens']
        signed_wallets = callparams['function_caller']
        lender = callparams["lender"]
        function_caller = {}
        custodian_present = False

        if len(signed_wallets) != 2:
            raise ContractValidationError("Only two signatures are required")
        for i in signed_wallets:
            if i["wallet_address"] == custodian_address:
                custodian_present = True
            else:
                function_caller = i["wallet_address"]
        if not custodian_present:
            raise ContractValidationError("Custodian signatures are mandatory")

        for i in tokens:
            if i in callparams["value"]:
                for j in callparams["value"]:
                    if j["token_code"]==i["token_code"] and j["amount"]==i["amount"]:
                        callparams["value"].pop(j)
                        break
                qparam = {"borrower": function_caller,
                          "address": self.address,
                          "lender": lender,
                          "token_code": i["token_code"]
                          }
                count = repo.select_count().add_table_name("pledge_ledger").where_clause("borrower", function_caller,
                                                                                         1).and_clause("address",
                                                                                                       self.address).and_clause(
                    "lender", lender).and_clause("token_code", i["token_code"]).execute_query_single_result(
                    qparam)
                if tokens["i"]['amount'] < 0:
                    raise ContractValidationError("amount shall be positive for token code %s" % i)
                value = function_caller + lender + i["token_code"]
                result = hashlib.sha256(value.encode()).hexdigest()
                if count[0] == 0:
                    sc_state_proposal1_data = {
                        "operation": "save",
                        "table_name": "pledge_ledger",
                        "sc_address": self.address,
                        "data": {
                            "borrower": function_caller,
                            "amount": tokens["i"]['amount'],
                            "time_updated": get_corrected_time_ms(),
                            "lender": lender,
                            "token_code": i["token_code"],
                            "unique_column": result,
                            "status": 1
                        }
                    }
                    transaction_creator = TransactionCreator()
                    txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                    trxn.append(txtype1)
                else:
                    amount = repo.select_Query("id,amount").add_table_name("pledge_ledger").where_clause("borrower",
                                                                                                         function_caller,
                                                                                                         1).and_clause(
                        "address", self.address).and_clause("lender", lender).and_clause("token_code", i[
                        "token_code"]).execute_query_single_result(
                        qparam)
                    if count[0] == 1:
                        sc_state_proposal1_data = {
                            "operation": "update",
                            "table_name": "pledge_ledger",
                            "sc_address": self.address,
                            "data": {
                                "amount": amount[1] + tokens["i"]['amount'],
                                "time_updated": get_corrected_time_ms()
                            },
                            "unique_column": "id",
                            "unique_value": amount[0],
                        }
                        transaction_creator = TransactionCreator()
                        txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                        trxn.append(txtype1)
                    else:
                        raise ContractValidationError("more than one record found")
        return trxn

    def unpledge_tokens(self, callparamsip, repo: FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        wallet_address = callparams["borrower_wallet"]
        lender = callparams["lender"]
        tokens = callparams["tokens"]
        for i in tokens:

            qparam = {"borrower": wallet_address,
                      "address": self.address,
                      "lender": lender,
                      "token_code": i["token_code"]
                      }
            count = repo.select_count().add_table_name("pledge_ledger").where_clause("borrower", wallet_address,
                                                                                     1).and_clause("address",
                                                                                                   self.address).and_clause(
                "lender", lender).and_clause("token_code", i["token_code"]).execute_query_single_result(
                qparam)
            if count[0] == 0:
                raise ContractValidationError("No pledge record found ofr tokencode %s" % i["token_code"])

            data = repo.select_Query("id,amount").add_table_name("pledge_ledger").where_clause("borrower",
                                                                                               wallet_address,
                                                                                               1).and_clause("address",
                                                                                                             self.address).and_clause(
                "lender", lender).and_clause("token_code", i["token_code"]).execute_query_single_result(
                qparam)
            if i["amount"] > data[1]:
                raise ContractValidationError(
                    "token amount for token code %s is greater than pledged amount" % i["token_code"])
            transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": i["token_code"],
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": wallet_address,
                "asset1_number": int(i["amount"]),
                "asset2_number": 0,
                "additional_data": {}
            }
            transaction_creator = TransactionCreator()
            trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "pledge_ledger",
                "sc_address": self.address,
                "data": {
                    "amount": int(math.floor(data[1] - i["amount"])),
                    "time_updated": get_corrected_time_ms(),
                },
                "unique_column": "id",
                "unique_value": data[0]
            }
            transaction_creator = TransactionCreator()
            txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
            trxn.append(txtype1)
        return trxn

    def default_tokens(self, callparamsip, repo: FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        wallet_address = callparams["borrower_wallet"]
        lender = callparams["lender"]
        token_code = callparams["token_code"]
        qparam = {"borrower": wallet_address,
                  "address": self.address,
                  "lender": lender,
                  "token_code": token_code
                  }
        count = repo.select_count().add_table_name("pledge_ledger").where_clause("borrower", wallet_address,
                                                                                 1).and_clause("address",
                                                                                               self.address).and_clause(
            "lender", lender).and_clause("token_code", token_code).execute_query_single_result(
            qparam)
        if count[0] == 0:
            raise ContractValidationError("No pledge record found ofr tokencode %s" % token_code)

        data = repo.select_Query("id,amount").add_table_name("pledge_ledger").where_clause("borrower",
                                                                                           wallet_address,
                                                                                           1).and_clause("address",
                                                                                                         self.address).and_clause(
            "lender", lender).and_clause("token_code", token_code).execute_query_single_result(
            qparam)
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": token_code,
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": lender,
            "asset1_number": data[2],
            "asset2_number": 0,
            "additional_data": {}
        }
        transaction_creator = TransactionCreator()
        trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
        sc_state_proposal1_data = {
            "operation": "update",
            "table_name": "pledge_ledger",
            "sc_address": self.address,
            "data": {
                "amount": 0,
                "time_updated": get_corrected_time_ms(),
                "status":2
            },
            "unique_column": "id",
            "unique_value": data[0]
        }
        transaction_creator = TransactionCreator()
        txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
        trxn.append(txtype1)
        pass

    def __get_pid_from_wallet_using_repo(self, repo: FetchRepository, address):
        pid = repo.select_Query('person_id').add_table_name('person_wallet').where_clause('wallet_id', address,
                                                                                          1).execute_query_single_result(
            {'wallet_id': address})

        if pid:
            return pid[0]
        return None
#
