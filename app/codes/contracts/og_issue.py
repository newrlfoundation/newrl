

import math
from re import T
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from app.nvalues import ZERO_ADDRESS
from .contract_master import ContractMaster
from app.codes.utils import get_last_block_hash


class og_issue(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "og_issue"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    


    def issue(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        callparams = input_to_dict(callparamsip)
        recipient_address = callparams['recipient_address']
        amount = callparams['amount']

        child_transactions = []
        token_name = cspecs['issuance_token_name']
        token_code = cspecs['issuance_token_code']
        function_caller = callparams['function_caller'][0]['wallet_address']

        # Check moved to signatories
        # issuer = cspecs['issuer']
        # if issuer != function_caller:
        #     raise Exception("Caller is not authorized")

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
        current_time = get_last_block_hash()["timestamp"]
        if not current_time >= exchange_start_date:
            raise Exception("Exchange is not allowed yet")

        issuance_token_code = cspecs['issuance_token_code']
        og_unstake_token_code = cspecs['og_unstake_token_code']

        token_multiplier = cspecs['token_exchange_multiplier']
        value = callparams['value']
        recipient_address = callparams['recipient_address']
        amount_to_issue = value[0]['amount']

        amount = amount_to_issue*token_multiplier

        ogfl_token_code = cspecs['ogfl_token_code']
        ogfl_token_name = cspecs['ogfl_token_name']

        required_value = {
            "token_code": issuance_token_code,
            "amount": amount_to_issue
        }

        required_value_unstake_coin = {
            "token_code": og_unstake_token_code,
            "amount": amount_to_issue
        }


        if required_value in value or required_value_unstake_coin in value:
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

            #type 2 to create og for life token
            transaction_creator = TransactionCreator()
            tokendata = {
                "tokenname": ogfl_token_name,
                "tokencode": ogfl_token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": recipient_address,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": 1,
                "value_created": '',
                "disallowed": {},
                "sc_flag": True,
            }
            ogfl = transaction_creator.transaction_type_two(tokendata)
        else:
            raise Exception("Incorrect txn value sent")    
        return [transfer_proposal, ogfl]
    
    def remove(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        withdraw_address = cspecs['withdraw_address']
        amount = callparams['amount']
       
        # Check moved to signatories
        # issuer = cspecs['issuer']
        # if issuer != function_caller:
        #     raise Exception("Caller is not authorized")

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
        og_token_name = cspecs['issuance_token_name']
        og_token_code = cspecs['issuance_token_code']

        ogfl_token_code = cspecs['ogfl_token_code']
        ogfl_token_name = cspecs['ogfl_token_name']

        child_transactions = []

        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": og_token_name,
            "tokencode": og_token_code,
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
        child_transactions.append(
               transaction_creator.transaction_type_two(tokendata))
        
        
        #type 2 to create og for life token
        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": ogfl_token_name,
            "tokencode": ogfl_token_code,
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
        ogfl = transaction_creator.transaction_type_two(tokendata)
        child_transactions.append(ogfl)

        return child_transactions    
    #validate
    # issue
    #   correct token as part of value
    # exchange
    #   correct token as part of value
    #   enough balance in the contract  