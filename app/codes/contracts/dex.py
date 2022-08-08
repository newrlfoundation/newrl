

from re import T
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from app.nvalues import ZERO_ADDRESS
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

        # liquidity_initialized = cspecs['liquidity_initialized']
        
        # if liquidity_initialized:
        #     raise Exception("Liquidity for this contract is already initialized, can't initialise it again")

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
        #ot issue amount will be the geometic mean of submited initial liquidity
        initial_ot_to_issue = (token_1_amount*token_2_amount)**(1/2)
        value = callparams['value']
        if not is_ratio_same(token_ratio,token_1_amount,token_2_amount):
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

        ot_token_code = cspecs['ot_token_code']
        ot_token_name = cspecs['ot_token_name']

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
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        #TODO validate

        callparams = input_to_dict(callparamsip)
        recipient_address = callparams['recipient_address']

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']

        #fetch token balance 1
        pool_token1_balance = self._fetch_token_balance(pool_token1_code, repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code, repo)

        fee = cspecs['fee']
        product = pool_token1_balance * pool_token2_balance
        token_sent = callparams['token_sent']
        token_asked = callparams['token_asked']
        recipient_address = callparams['recipient_address']

        if token_sent["token_code"] == pool_token1_code:
            new_token1_balance = pool_token1_balance + token_sent["amount"]
            new_token2_balance = product / new_token1_balance
            token_amount_to_send = pool_token2_balance - new_token2_balance
        else:    
            new_token2_balance = pool_token2_balance + token_sent["amount"]
            new_token1_balance = product / new_token2_balance
            token_amount_to_send = pool_token1_balance - new_token1_balance

        #add fee    
        tokens_to_send = (1 - fee )*token_amount_to_send

        required_value = {
            "token_code": token_sent["token_code"],
            "amount": token_sent["amount"]
        }

        value = callparams['value']
        if not required_value in value:
            raise Exception("Invalid value sent")        

        '''txn type 5 '''
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": token_asked["token_code"],
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": recipient_address,
            "asset1_number": tokens_to_send,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal = transaction_creator.transaction_type_5(transfer_proposal_data)
        return [transfer_proposal]

    def withdraw(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)
        withdraw_amount = callparams['withdraw_amount']
        recipient_address = callparams['recipient_address']

        ot_token_code = cspecs['ot_token_code']
        ot_outstanding = self._get_outstanding_ot(ot_token_code, repo)

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']

        #fetch token balance 1
        pool_token1_balance = self._fetch_token_balance(pool_token1_code, repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code, repo)

        token1_withdraw_amount = (pool_token1_balance * withdraw_amount ) / ot_outstanding
        token2_withdraw_amount = (pool_token2_balance * withdraw_amount) / ot_outstanding

        required_value = {
            "token_code": ot_token_code,
            "amount" : withdraw_amount
        }

        value = callparams['value']
        if not required_value in value:
            raise Exception("Value sent is invalid")

        # #A txn 5 to send tokens to address 0 to burn (assuming value txn happens before this)
        # '''txn type 5 (burn)'''
        # transaction_creator = TransactionCreator()
        # transfer_proposal_data = {
        #     "transfer_type": 1,
        #     "asset1_code": ot_token_code,
        #     "asset2_code": "",
        #     "wallet1": self.address,
        #     "wallet2": ZERO_ADDRESS,
        #     "asset1_number": withdraw_amount,
        #     "asset2_number": 0,
        #     "additional_data": {}
        # }
        # transfer_proposal_burn = transaction_creator.transaction_type_5(
        #     transfer_proposal_data)

        #A txn 5 to send pool token1 to recipient 
        '''txn type 5 token1'''
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": pool_token1_code,
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": recipient_address,
            "asset1_number": token1_withdraw_amount,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal_token1 = transaction_creator.transaction_type_5(
            transfer_proposal_data)

        #A txn 5 to send pool token2 to recipient
        '''txn type 5 token2'''
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": pool_token2_code,
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": recipient_address,
            "asset1_number": token2_withdraw_amount,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal_token2 = transaction_creator.transaction_type_5(
            transfer_proposal_data)

        return [transfer_proposal_token1,transfer_proposal_token2]


    def _fetch_token_balance(self,token_code,repo):
        
        balance = repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address", self.address, 1).and_clause(
            "tokencode", token_code,1).execute_query_single_result({"wallet_address": self.address,"tokencode":token_code})
        return balance[0]    
        
    def _get_ot_issue(self,ot_outstanding, token_1_amount, token_2_amount, pool_token1_balance, pool_token2_balance):
        t1 = token_1_amount / (pool_token1_balance)
        t2 = token_2_amount / (pool_token2_balance)
        ot_to_issue = ot_outstanding * min(t1, t2)
        return ot_to_issue

    def _get_outstanding_ot(self,token_code,repo: FetchRepository):
        balance = repo.select_sum("balance").add_table_name("balances").where_clause("tokencode", token_code, 1).and_clause("wallet_address",self.address, 5).execute_query_single_result({"tokencode": token_code,"wallet_address": self.address})
        return balance[0]

    def validate(self, callparamsip, repo: FetchRepository):
        pass


def is_ratio_same(pool_ratio_st, token1, token2):
    #assumes pool ratio is of type string "x:y"
    ratio = [int(i) for i in pool_ratio_st.split(":") if i.isdigit()]
    pool_ratio = ratio[0]/ratio[1]
    token_ratio = token1/token2
    return pool_ratio.as_integer_ratio() == token_ratio.as_integer_ratio()
