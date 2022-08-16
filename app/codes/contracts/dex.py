

import math
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

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']
       
        recipient_address = callparams['recipient_address']
        value = callparams['value']
        tokens = self._get_input_tokens(value,pool_token1_code, pool_token2_code)
        token_1 = tokens["token_1"]
        token_2 = tokens["token_2"]

        token_1_amount = token_1["amount"]
        token_2_amount = token_2["amount"]

        ot_token_code = cspecs['ot_token_code']
        ot_token_name = cspecs['ot_token_name']

        token_ratio = cspecs['token_ratio']
        if not self._is_ratio_same(token_ratio, token_1_amount, token_2_amount):
            raise Exception(f"Provided token ratio is not correct, should be of ratio {token_ratio}")
        
        #ot issue amount will be the geometic mean of submited initial liquidity
        initial_ot_to_issue = math.floor((token_1_amount*token_2_amount)**(1/2))
        value = callparams['value']


        # if required_value_token1 in value and required_value_token2 in value:
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
 



    def provide_liquidity(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        callparams = input_to_dict(callparamsip)

        recipient_address = callparams['recipient_address']
 
        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']
        #fetch token balance 1
        pool_token1_balance = self._fetch_token_balance(pool_token1_code, self.address,repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code, self.address, repo)

        value = callparams['value']
        tokens = self._get_input_tokens(
            value, pool_token1_code, pool_token2_code)
        token_1 = tokens["token_1"]
        token_2 = tokens["token_2"]

        token_1_amount = token_1["amount"]
        token_2_amount = token_2["amount"]

        token_ratio = cspecs['token_ratio']
        if not self._is_ratio_same(token_ratio, token_1_amount, token_2_amount):
            raise Exception(f"Provided token ratio is not correct, should be of ratio {token_ratio}")


        ot_token_code = cspecs['ot_token_code']
        ot_token_name = cspecs['ot_token_name']

        ot_outstanding = self._get_outstanding_ot(ot_token_code, repo)
        ot_to_issue = math.floor(self._get_ot_issue(ot_outstanding, token_1_amount, token_2_amount, pool_token1_balance,pool_token2_balance))


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
  

    def swap(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        #TODO validate

        callparams = input_to_dict(callparamsip)
        recipient_address = callparams['recipient_address']

        pool_token1_code = cspecs['pool_token1_code']
        pool_token2_code = cspecs['pool_token2_code']

        #fetch token balance 1
        pool_token1_balance = self._fetch_token_balance(pool_token1_code,self.address, repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code,self.address, repo)

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

        #fee in aboslute Ex : 1% will be provided as 0.01 
        #TODO check determistic logic for rounding , parse to int (floor it)
        tokens_to_send = math.floor((1 - fee )*token_amount_to_send)

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
        pool_token1_balance = self._fetch_token_balance(pool_token1_code,self.address, repo)
        #fetch token balance 2
        pool_token2_balance = self._fetch_token_balance(pool_token2_code,self.address, repo)
        #TODO INT

        if withdraw_amount == ot_outstanding:
            token1_withdraw_amount = pool_token1_balance
            token2_withdraw_amount = pool_token2_balance
        else:    
            token1_withdraw_amount = math.floor((pool_token1_balance * withdraw_amount ) / ot_outstanding)
            token2_withdraw_amount = math.floor((pool_token2_balance * withdraw_amount) / ot_outstanding)

        required_value = {
            "token_code": ot_token_code,
            "amount" : withdraw_amount
        }

        value = callparams['value']
        if not required_value in value:
            raise Exception("Value sent is invalid")

        child_transactions = []
        current_self_ot_outstanding = self._fetch_token_balance(ot_token_code, self.address,repo)

        # logger.info(f"token 1 and 2 amounts being redeemed are {token1_withdraw_amount} , {token2_withdraw_amount}")

        # #A txn 5 to send tokens (burn) previous outstanding tokens to address 0 to burn (assuming value txn happens before this)
        # #TODO add zero address in db init
        # if current_self_ot_outstanding > 0:
        #     '''txn type 5 (burn)'''
        #     transaction_creator = TransactionCreator()
        #     transfer_proposal_data = {
        #         "transfer_type": 1,
        #         "asset1_code": ot_token_code,
        #         "asset2_code": "",
        #         "wallet1": self.address,
        #         "wallet2": ZERO_ADDRESS,
        #         "asset1_number": current_self_ot_outstanding,
        #         "asset2_number": 0,
        #         "additional_data": {}
        #     }
        #     transfer_proposal_burn = transaction_creator.transaction_type_5(
        #         transfer_proposal_data)
        #     child_transactions.append(transfer_proposal_burn)

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
        child_transactions.append(transfer_proposal_token1)

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
        child_transactions.append(transfer_proposal_token2)

        return child_transactions

    def _fetch_token_balance(self,token_code,address, repo):
        
        balance = repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address", address, 1).and_clause(
            "tokencode", token_code,1).execute_query_single_result({"wallet_address": address,"tokencode":token_code})
        if balance == None:
            return 0  
        return balance[0]      
        
    def _get_ot_issue(self,ot_outstanding, token_1_amount, token_2_amount, pool_token1_balance, pool_token2_balance):
        t1 = token_1_amount / (pool_token1_balance)
        t2 = token_2_amount / (pool_token2_balance)
        ot_to_issue = ot_outstanding * min(t1, t2)
        return ot_to_issue

    def _get_outstanding_ot(self,token_code,repo: FetchRepository):
        balance = repo.select_sum("balance").add_table_name("balances").where_clause("tokencode", token_code, 1).and_clause("wallet_address",self.address, 5).execute_query_single_result({"tokencode": token_code,"wallet_address": self.address})
        return balance[0]

    def _validate(self, callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        method = callparams['function']
        function_caller = callparams['function_caller']
        if method == "initialise_liquidity":
            '''
            Check if sender has sent correct token codes as per pool
            Check if enough blance of those tokens is present
            '''
            cspecs = input_to_dict(self.contractparams['contractspecs'])
            pool_token1_code = cspecs['pool_token1_code']
            pool_token2_code = cspecs['pool_token2_code']
            provided_tokens = self._get_input_tokens(
                callparams["value"], pool_token1_code, pool_token2_code)
            if not self._is_having_balance(function_caller, provided_tokens["token_1"]["token_code"], provided_tokens["token_1"]["amount"], repo):
                raise Exception(f"Insufficient funds for {pool_token1_code}")
            if not self._is_having_balance(function_caller,provided_tokens["token_2"]["token_code"], provided_tokens["token_2"]["amount"], repo):
                raise Exception(f"Insufficient funds for {pool_token2_code}")
            pass
        elif method == "provide_liquidity":
            '''
            Check if sender has sent correct token codes as per pool 
            Check if enough blance of those tokens is present
            '''
            cspecs = input_to_dict(
            self.contractparams['contractspecs'])
            pool_token1_code = cspecs['pool_token1_code']
            pool_token2_code = cspecs['pool_token2_code']
            provided_tokens = self._get_input_tokens(
                callparams["value"], pool_token1_code, pool_token2_code)
            if not self._is_having_balance(function_caller, provided_tokens["token_1"]["token_code"], provided_tokens["token_1"]["amount"], repo):
                raise Exception(f"Insufficient funds for {pool_token1_code}")
            if not self._is_having_balance(function_caller,provided_tokens["token_2"]["token_code"], provided_tokens["token_2"]["amount"], repo):
                raise Exception(f"Insufficient funds for {pool_token2_code}")
            pass
        elif method == "swap":
            '''
            Check if token sent as part of value is present in pool
            Check if  pool is having enough balance to be sent
            Check if enough blance of those tokens is present
            '''
            cspecs = input_to_dict(self.contractparams['contractspecs'])
            pool_token1_code = cspecs['pool_token1_code']
            pool_token2_code = cspecs['pool_token2_code']
            provided_tokens = self._get_input_tokens(callparams["value"], pool_token1_code, pool_token2_code)

            if provided_tokens["token_1"] == {}:
                if not self._is_having_balance(function_caller, provided_tokens["token_2"]["token_code"], provided_tokens["token_1"]["amount"], repo):
                    raise Exception(f"Insufficient funds for {pool_token2_code}")
            if provided_tokens["token_2"] == {}:
                if not self._is_having_balance(function_caller, provided_tokens["token_1"]["token_code"], provided_tokens["token_1"]["amount"], repo):
                    raise Exception(
                        f"Insufficient funds for {pool_token1_code}")
            #TODO cal token to be given and check if pool is having enough balance            
            pass
        elif method == "withdraw":
            '''
            Check if ot token sent is correct ot token of this pool
            Check if enough blance of those tokens is present
            '''
            cspecs = input_to_dict(self.contractparams['contractspecs'])
            ot_token_code = cspecs['ot_token_code']
            ot_value = {}
            for value in callparams["value"]:
                if value["token_code"] == ot_token_code:
                    ot_value = value
            if ot_value == {}:
                raise Exception(
                "tokens sent as part of value is invalid")
            if not self._is_having_balance(function_caller, ot_token_code, ot_value["amount"],repo):
                raise Exception(f"Insufficient funds for {ot_token_code}")

            pass
        else:
            raise Exception(f"provived function {method} is not supported and could not be validated")


    def _is_ratio_same(self,pool_ratio_st, token1, token2):
        #assumes pool ratio is of type string "x:y"
        ratio = [int(i) for i in pool_ratio_st.split(":") if i.isdigit()]
        pool_ratio = ratio[0]/ratio[1]
        token_ratio = token1/token2
        return pool_ratio.as_integer_ratio() == token_ratio.as_integer_ratio()

    def _is_having_balance(self,address,token_code,req_balance,repo: FetchRepository):
        balance = self._fetch_token_balance(address,token_code,repo)
        if balance == req_balance:
            return True
        else:
            return False    

    def _get_input_tokens(self, values, pool_token_1_code, pool_token_2_code):
        token_1 = {}
        token_2 = {}

        for value in values:
            if value["token_code"] == pool_token_1_code:
                token_1 = value
            elif value["token_code"] == pool_token_2_code:
                token_2 = value
        if token_1 == {} or token_2 == {}:
            raise Exception("tokens sent as part of value is invalid or not present")
       
        return{
            "token_1": token_1,
            "token_2": token_2
        }