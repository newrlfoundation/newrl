import json
import math
from app.core.contracts.contract_master import ContractMaster
from app.core.contracts.dao_main_template import DaoMainTemplate
from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator


class crowd_funding_contract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "crowd_funding_contract"
        self.version = "1.0.0"
        self.dao_type = 2
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    def invest(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        goal_amount = cspecs['goal_amount']
        minimum_amount = cspecs['minimum_amount']

        
        value = callparams['value']

        existing_fund = self._fetch_fund(repo)


        status = existing_fund["status"] if existing_fund is not None else None

        unit_price = cspecs['unit_price']
        amount = value[0]['amount']

        unit_currency = cspecs['unit_currency']

        if value[0]['amount'] < minimum_amount:
            raise Exception("Minimum amount criteria not satisfied")
        if existing_fund and existing_fund["amount_raised"] >= goal_amount:
            raise Exception("goal amount already reached")
        
        if value[0]["token_code"] != unit_currency:
            raise Exception("Invalid tokens sent as part of value")

        #TODO 
        goal_reached = False

        child_transactions = []

        #TODO else logic
        if not existing_fund:
            investor_data = {
                callparams['function_caller'][0]['wallet_address'] : amount
            }
            state_data = {
                "address":self.address,
                "amount_raised" : amount,
                "status":"open",
                "investor": json.dumps(investor_data)
            }

            sc_state_proposal1_data = {
                "operation": "save",
                "table_name": "crowd_funding",
                "sc_address": self.address,
                "data": state_data
            }
            transaction_creator = TransactionCreator()
            add_fundung_proposal = transaction_creator.transaction_type_8(
                sc_state_proposal1_data)
            child_transactions.append(add_fundung_proposal)
        else:
            if goal_reached:
                existing_fund["status"] = "goal_reached"
            existing_fund["amount_raised"] = amount + existing_fund["amount_raised"]
            current_investors = existing_fund["investor"]
            current_investors[callparams['function_caller'][0]['wallet_address']] = amount
            existing_fund["investor"]= json.dumps(current_investors)
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "crowd_funding",
                "sc_address": self.address,
                "data": existing_fund,
                "unique_column": "address",
                "unique_value": self.address
            }
            transaction_creator = TransactionCreator()
            add_fundung_proposal = transaction_creator.transaction_type_8(
                sc_state_proposal1_data)
            child_transactions.append(add_fundung_proposal)
            
        return child_transactions

    def create_master_token(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        benefeciary = cspecs['benefeciary_address']
        master_token_code = cspecs['master_token_code']

        existing_fund = self._fetch_fund(repo)

        #check if goal is complete TODO

        if not existing_fund:
            raise Exception("No investments found for this fund")
        
        child_transactions = []

        #create master token
        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": master_token_code,
            "tokencode": master_token_code,
            "tokentype": '1',
            "tokenattributes": {},
            "first_owner": benefeciary,
            "custodian": self.address,
            "legaldochash": '',
            "amount_created": 1,
            "value_created": '',
            "disallowed": {},
            "sc_flag": True,
        }
        create_proposal = transaction_creator.transaction_type_two(
            tokendata)
        child_transactions.append(create_proposal)

        #trasnfer master and ninr to benefeciary
        #TODO seperate fee part and send only raw
        ninr_to_send = existing_fund["amount_raised"]
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "asset1_code": "NWRL",
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": benefeciary,
            "asset1_number": ninr_to_send,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal = transaction_creator.transaction_type_5(
            transfer_proposal_data)
        child_transactions.append(transfer_proposal)

        return child_transactions

    def create_mirror_token(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        benefeciary = cspecs['benefeciary_address']
        mirror_token_code = cspecs['mirror_token_code']

        existing_fund = self._fetch_fund(repo)

        #check if goal is complete TODO

        if not existing_fund:
            raise Exception("No investments found for this fund")
        
        child_transactions = []

        investors = existing_fund["investor"]

        for investor in investors:
            #create mirror token
            transaction_creator = TransactionCreator()
            tokendata = {
                "tokenname": mirror_token_code,
                "tokencode": mirror_token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": investor,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": investors[investor],
                "value_created": '',
                "disallowed": {},
                "sc_flag": True,
            }
            create_proposal = transaction_creator.transaction_type_two(
                tokendata)
            child_transactions.append(create_proposal)

        return child_transactions



    # def get_startup_tokens(self, callparamsip, repo: FetchRepository):
    #     cspecs = input_to_dict(self.contractparams['contractspecs'])
    #     callparams = input_to_dict(callparamsip)

    #     pledge_token_code = cspecs['pledge_token_code']

    #     company_token_name = cspecs['company_token_name']
    #     company_token_code = cspecs['company_token_code']

    #     recipient_address = callparams['recipient_address']

    #     # super.issue_token()
    #     value = callparams['value']
    #     if value[0]["token_code"] != pledge_token_code:
    #         raise Exception("Invalid tokens sent as part of value")

    #     amount = value[0]['amount']

    #     child_transactions = []
    #     transaction_creator = TransactionCreator()
    #     tokendata = {
    #         "tokenname": company_token_name,
    #         "tokencode": company_token_code,
    #         "tokentype": '1',
    #         "tokenattributes": {},
    #         "first_owner": recipient_address,
    #         "custodian": self.address,
    #         "legaldochash": '',
    #         "amount_created": amount,
    #         "value_created": '',
    #         "disallowed": {},
    #         "sc_flag": True,
    #     }
    #     child_transactions.append(
    #         transaction_creator.transaction_type_two(tokendata))
    #     return child_transactions

    def get_total_issued_tokens(self, token_code, repo):
        balance = repo.select_sum("balance").add_table_name("balances").where_clause(
            "tokencode", token_code, 1).execute_query_single_result({"tokencode": token_code, "wallet_address": self.address})
        if balance[0] is None:
            return 0
        else:
            return balance[0]

    def _fetch_token_balance(self, token_code, address, repo):
        balance = repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address", address, 1).and_clause(
            "tokencode", token_code, 1).execute_query_single_result({"wallet_address": address, "tokencode": token_code})
        if balance == None:
            return 0
        return balance[0]
    
    def _fetch_fund(self, repo):
        state = repo.select_Query().add_table_name('crowd_funding').where_clause('address', self.address,
                                                                                          1).execute_query_single_result(
            {'address': self.address})
        
        existing_fund = {}
        if state is not None:
            existing_fund["address"] = state[0]
            existing_fund["amount_raised"] = state[1]
            existing_fund["status"] = state[2]
            existing_fund["investor"] = json.loads(state[3])
        return existing_fund