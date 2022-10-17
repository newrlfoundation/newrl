

import math
from re import T
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from app.nvalues import ZERO_ADDRESS
from .contract_master import ContractMaster


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

        issuance_token_code = cspecs['issuance_token_code']
        token_multiplier = cspecs['token_multiplier']
        value = callparams['value']
        recipient_address = callparams['recipient_address']
        amount_to_issue = value[0]['amount']

        amount = amount_to_issue*token_multiplier

        required_value = {
            "token_code": issuance_token_code,
            "amount": amount_to_issue
        }

        if required_value in value:
            '''txn type 5 (one way transfer)'''
            transaction_creator = TransactionCreator()
            transfer_proposal_data = {
                "transfer_type": 1,
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
        return [transfer_proposal]
    
    def remove(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        withdraw_address = cspecs['withdraw_address']
        amount = callparams['amount']

        function_caller = callparams['function_caller'][0]['wallet_address']
       
        # Check moved to signatories
        # issuer = cspecs['issuer']
        # if issuer != function_caller:
        #     raise Exception("Caller is not authorized")

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