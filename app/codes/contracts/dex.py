

from re import T
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
        
        if liquidity_initialized:
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

        token_ratio = cspecs['token_ratio']
        #issue min of tokens that will be issued? as this is the amount that will be in circulation later on
        initial_ot_to_issue = cspecs['initial_ot_to_issue']
        value = callparams['value']
        provided_ratio = token_1_amount/token_2_amount
        if not provided_ratio == token_ratio:
         raise Exception(f"Provided token ratio is not correct, should be of ratio {token_ratio}")

        if required_value_token1 in value and required_value_token2 in value:
            tokendata = {
                "tokenname": ot_token_name,
                "tokencode": ot_token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": recipient_address,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": initial_ot_to_issue,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            
            transacation_creator = TransactionCreator()
            transaction = transacation_creator.transaction_type_two(tokendata)
            return [transaction]
        else:
            raise Exception("Value sent is invalid") 



    def provide_liquidity(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        callparams = input_to_dict(callparamsip)
        token_1_amount = callparams['token_1_amount'] 
        token_2_amount  = callparams['token_2_amount']
        recipient_address = callparams['recipient_address']

        provided_ratio = token_1_amount/token_2_amount
 
        ot_token_code = cspecs['ot_token_code']
        ot_token_name = cspecs['ot_token_name']

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']

        #fetch token balance 1
        pool_token1_balance = self._fetch_token_balance(pool_token1_code, repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code, repo)

        token_ratio = pool_token1_balance/pool_token2_balance
        if not provided_ratio == token_ratio:
            raise Exception(
                f"Provided token ratio is not correct, should be of ratio {token_ratio}")

        ot_outstanding = self._get_outstanding_ot(ot_token_code, repo)
        ot_to_issue = self._get_ot_issue(ot_outstanding, token_1_amount, token_2_amount, pool_token1_balance,pool_token2_balance)

        required_value_token1 = {
            "token_code": pool_token1_code,
            "amount": token_1_amount
        }

        required_value_token2 = {
            "token_code": pool_token2_code,
            "amount": token_2_amount
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
        
    def _get_ot_issue(self,ot_outstanding, token_1_amount, token_2_amount, pool_token1_balance, pool_token2_balance):
        t1 = token_1_amount / (pool_token1_balance)
        t2 = token_2_amount / (pool_token2_balance)
        ot_to_issue = ot_outstanding * min(t1, t2)
        return ot_to_issue

    def _get_outstanding_ot(self,token_code,repo: FetchRepository):
        balance = repo.select_count("balance").add_table_name("balances").where_clause("token_code", token_code, 1).execute_query_single_result({"token_code":token_code})
        return balance

