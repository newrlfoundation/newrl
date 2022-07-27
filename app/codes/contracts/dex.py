

from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from .contract_master import ContractMaster


class dex(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "dex"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    

    def initialise_liquidity(self,callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        
        #transfer amount to liquidity
        callparams = input_to_dict(callparamsip)
        #dex liquidity shouldnt be initalised already

        liquidity_initialized = cspecs['liquidity_initialized']
        
        if not liquidity_initialized:
            raise Exception("Liquidity for this contract is already initialized, can't initialise it again")

        token_1_amount = callparams['token_1_amount'] 
        token_2_amount  = callparams['token_2_amount']
        recipient_address = callparams['recipient_address']

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']

        required_value_token1 = {
            "token_code": pool_token1_code,
            "amount": token_1_amount
        }

        required_value_token2 = {
            "token_code": pool_token2_code,
            "amount": token_2_amount
        }

        ot_token_code = cspecs['ot_token_code']
        ot_token_name = cspecs['ot_token_name']

        ot_to_issue = min(token_1_amount,token_2_amount)

        value = callparams['value']
        if required_value_token1 in value and required_value_token2 in value:
            tokendata = {
                "tokenname": ot_token_name,
                "tokencode": ot_token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": recipient_address,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": ot_to_issue,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            
            transacation_creator = TransactionCreator()
            transaction = transacation_creator.transaction_type_two(tokendata)
            return [transaction]
        else:
            raise Exception("Value sent is invalid") 
        pass

    def provide_liquidity(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        callparams = input_to_dict(callparamsip)
        token_1_amount = callparams['token_1_amount'] 
        token_2_amount  = callparams['token_2_amount']
        recipient_address = callparams['recipient_address']

        ot_token_code = cspecs['ot_token_code']
        ot_token_name = cspecs['ot_token_name']

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']

        #TODO check if tokens sent is part of pool

        #fetch token balance 1
        pool_token1_balance = self._fetch_token_balance(pool_token1_code, repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code, repo)
        #ratio
        ratio = pool_token1_balance / pool_token2_balance

        ot_outstanding = self._fetch_token_balance(ot_token_code, repo)
        ot_to_issue = ot_outstanding * (token_1_amount/pool_token1_balance)

        required_value_token1 = {
            "token_code": pool_token1_code,
            "amount": 1
        }

        required_value_token2 = {
            "token_code": pool_token2_code,
            "amount": 1
        }
        value = callparams['value']
        if required_value_token1 in value and required_value_token2 in value:
            tokendata = {
                "tokenname": ot_token_name,
                "tokencode": ot_token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": recipient_address,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": ot_to_issue,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            
            transacation_creator = TransactionCreator()
            transaction = transacation_creator.transaction_type_two(tokendata)
            return [transaction]
        else:
            raise Exception("Value sent is invalid")    


# 10 10
# OTO = 0
# T1a = 10
# T2a = 10
# T1PB = 0

# 0*(10/O)



# 10 10 
# OTO = 20
# T1a = 10
# T2a = 10
# T1PB = 0

# 0*(10/O)
    def swap(self, callparamsip, repo: FetchRepository):
        pass

    def exit_pool(self, callparamsip, repo: FetchRepository):
        pass

    def provide_liquidity(self, callparamsip, repo: FetchRepository):
        pass

    def validate(self, callparamsip, repo: FetchRepository):
        pass

    def _fetch_token_balance(self,token_code,repo):
        
        balance = repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address", self.address, 1).and_clause(
            "tokencode", token_code).execute_query_single_result({"wallet_address": self.address,"tokencode":token_code})
                
        return balance    
        