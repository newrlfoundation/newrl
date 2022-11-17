

import math
from re import T
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from app.nvalues import ZERO_ADDRESS
from .contract_master import ContractMaster
from app.codes.utils import get_last_block_hash


class nlt(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "nlt"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    


    def issue(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        token_name = cspecs['issuance_token_name']
        token_code = cspecs['issuance_token_code']
        token_decimal = cspecs['token_decimal']
        max_supply = cspecs['max_supply']
        current_tokens_issued = self._get_outstanding(token_code,repo)
        amount = callparams['amount']

        if current_tokens_issued  + amount > max_supply :
            raise Exception(
                "Maximum supply has been reached, can't issue tokens for given amount")

        recipient_address = callparams['recipient_address']

        child_transactions = []

        for address in recipient_address:
           transaction_creator = TransactionCreator()
           tokendata = {
               "tokenname": token_name,
               "tokencode": token_code,
               "tokentype": '1',
               "tokenattributes": {},
               "first_owner": address,
               "custodian": self.address,
               "legaldochash": '',
               "amount_created": amount,
               "tokendecimal": token_decimal,
               "value_created": '',
               "disallowed": {},
               "sc_flag": True,
           }
           child_transactions.append(
               transaction_creator.transaction_type_two(tokendata))
        
        return child_transactions

    def exchange(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        exchange_start_date = cspecs['exchange_start_date']
        exchange_end_date = cspecs['exchange_end_date']

        current_time = get_last_block_hash()["timestamp"]

        if not current_time >= exchange_start_date:
            raise Exception("Exchange is not allowed yet")
        if not current_time <= exchange_end_date:
            raise Exception("Exchange is closed")

        issuance_token_code = cspecs['issuance_token_code']

        token_multiplier = cspecs['token_exchange_multiplier']
        value = callparams['value']
        recipient_address = callparams['recipient_address']
        amount_to_exchange = value[0]['amount']

    
        amount = amount_to_exchange*token_multiplier

        contract_balance = self._fetch_token_balance(
            "NWRL", self.address, repo)
        if contract_balance < amount:
            raise Exception("Insufficient balance in the contract")

        required_value = {
            "token_code": issuance_token_code,
            "amount": amount_to_exchange
        }


        if required_value in value :
            '''txn type 5 (one way transfer)'''
            transaction_creator = TransactionCreator()
            transfer_proposal_data = {
                "asset1_code": "NWRL",
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": recipient_address,
                "asset1_number": amount,
                "asset2_number": 0,
                "additional_data": {}
            }
            transfer_proposal = transaction_creator.transaction_type_5(
                transfer_proposal_data)

        else:
            raise Exception("Incorrect txn value sent")    
        return [transfer_proposal]
    
    def remove(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        withdraw_address = cspecs['withdraw_address']
        amount = callparams['amount']

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
    
    def burn(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        issuance_token_code = cspecs['issuance_token_code']
        nlp_token_balance = self._fetch_token_balance(issuance_token_code,self.address, repo)
        '''txn type 5 (one way transfer)'''
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "asset1_code": issuance_token_code,
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": ZERO_ADDRESS,
            "asset1_number": nlp_token_balance,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal = transaction_creator.transaction_type_5(
            transfer_proposal_data)

        return [transfer_proposal]

    def initialize_tokens(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        token_name = cspecs['issuance_token_name']
        token_code = cspecs['issuance_token_code']
        child_transactions = []
        token_decimal = cspecs['token_decimal']

        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": token_name,
            "tokencode": token_code,
               "tokentype": '1',
               "tokenattributes": {},
               "first_owner": self.address,
               "custodian": self.address,
               "legaldochash": '',
               "amount_created": 1,
               "tokendecimal": token_decimal,
               "value_created": '',
               "disallowed": {},
               "sc_flag": True,
           }
        child_transactions.append(
               transaction_creator.transaction_type_two(tokendata))
        
        return child_transactions    

    def _fetch_token_balance(self, token_code, address, repo):
        balance = repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address", address, 1).and_clause(
            "tokencode", token_code, 1).execute_query_single_result({"wallet_address": address, "tokencode": token_code})
        if balance == None:
            return 0
        return balance[0]

    def _get_outstanding(self, token_code, repo: FetchRepository):
        balance = repo.select_sum("balance").add_table_name("balances").where_clause("tokencode", token_code, 1).and_clause(
            "wallet_address", self.address, 5).execute_query_single_result({"tokencode": token_code, "wallet_address": self.address})
        if balance == None or balance[0] == None:
            return 0
        return balance[0]
