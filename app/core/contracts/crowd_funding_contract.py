import math
from app.core.contracts.contract_master import ContractMaster
from app.core.contracts.dao_main_template import DaoMainTemplate
from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator


class crowd_funding_dao(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "crowd_funding_dao"
        self.version = "1.0.0"
        self.dao_type = 2
        super().__init__(contractaddress)

    def invest(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        goal_amount = cspecs['goal_amount']
        minimum_amount = cspecs['minimum_amount']

        pledge_token_code = cspecs['pledge_token_code']
        current_outstanding = self.get_total_issued_tokens(
            pledge_token_code, repo)

        if current_outstanding >= goal_amount:
            raise Exception("goal amount already reached")

        unit_price = cspecs['unit_price']
        unit_currency = cspecs['unit_currency']

        value = callparams['value']
        if value[0]["token_code"] != unit_currency:
            raise Exception("Invalid tokens sent as part of value")

        amount = value[0]['amount']
        token_issue_amount = math.floor(amount/unit_price)

        recipient_address = callparams['recipient_address']

        #TODO have new sc state to track raised amount, status, time period?
        #TODO logic to check on time/min/max amount

        child_transactions = []
        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": pledge_token_code,
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

    def create_master_token(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        benefeciary = cspecs['pledge_token_code']
        master_token_code = cspecs['master_token_code']

        #check if goal is complete

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
        ninr_to_send = self._fetch_token_balance("NEWRL",self.address,repo)

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
