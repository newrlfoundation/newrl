import math
from app.codes.contracts.contract_master import ContractMaster
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator


class crowd_funding(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "dex"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    
    def invest(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        unit_price = cspecs['unit_price']
        unit_currency = cspecs['unit_currency']

        value = callparams['value']
        if value[0]["token_code"] != unit_currency:
            raise Exception("Invalid tokens sent as part of value")

        amount = value[0]['amount']
        token_issue_amount = math.floor(amount/unit_price)
        pledge_token_code = callparams['pledge_token_code']    
        pledge_token_name = callparams['pledge_token_name']
        recipient_address = callparams['recipient_address']

        #TODO have new sc state to track raised amount, status?

        child_transactions = []
        transaction_creator = TransactionCreator()
        tokendata = {
               "tokenname": pledge_token_name,
               "tokencode": pledge_token_code,
               "tokentype": '1',
               "tokenattributes": {},
               "first_owner": recipient_address,
               "custodian": self.address,
               "legaldochash": '',
               "amount_created": token_issue_amount,
               "value_created": '',
               "disallowed": {},
               "sc_flag": True,
           }
        child_transactions.append(
               transaction_creator.transaction_type_two(tokendata))
        return child_transactions
             
    def get_startup_tokens(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        pledge_token_code = callparams['pledge_token_code']
        
        company_token_name = cspecs['company_token_name']
        company_token_code = cspecs['company_token_code']

        recipient_address = callparams['recipient_address']
        amount = value[0]['amount']

        value = callparams['value']
        if value[0]["token_code"] != pledge_token_code:
            raise Exception("Invalid tokens sent as part of value")

        child_transactions = []
        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": company_token_name,
            "tokencode": company_token_code,
            "tokentype": '1',
            "tokenattributes": {},
            "first_owner": recipient_address,
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
