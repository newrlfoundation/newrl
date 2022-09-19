from .dao_main_template import DaoMainTemplate
from ..db_updater import *
import math

from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator


class token_fund_dao(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None):
        self.template= 'token_fund_dao'
        self.version='1.0.0'
        self.dao_type=2
        # dao_type=2 is for token based DAO and 1 is for membership DAO
        super().__init__(contractaddress)

    def invest(self,callparamsip,repo:FetchRepository):
        trxn=[]
        return trxn

    def disburse(self,callparamsip,repo:FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        tansaction_creator = TransactionCreator()
        qparam={
            "proposal_id":callparams["proposal_id"],
            "status":"accepted"
        }
        proposal_data=repo.select_Query("params").add_table_name("proposal_data").\
            where_clause("proposal_id",qparam["proposal_id"],1).and_clause("status",qparam["status"],1).execute_query_single_result(qparam)
        if proposal_data is not None:
            dao_id = self.address
            accepted_prop=input_to_dict(proposal_data[0])
            wallet_to_invest = accepted_prop['wallet_to_invest']
            token_to_invest_code = accepted_prop['invest_token_code']
            token_to_invest_amount = accepted_prop['invest_token_amount']
            token_to_recieve = accepted_prop['token_to_recieve']
            token_recieve_amt = accepted_prop['token_recieve_amt']
            # Transfering Tokens from User To DAO
            sender1 = wallet_to_invest
            sender2 = dao_id

            tokencode1 = token_to_invest_code
            amount1 = int(token_to_invest_amount or 0)
            value = callparams["value"]

            required_value = {
                "token_code": token_to_recieve,
                "amount": token_recieve_amt
            }

            if required_value in value:
                transfer_proposal_data = {
                    "transfer_type": 1,
                    "asset1_code": token_to_invest_code,
                    "asset2_code": "",
                    "wallet1": self.address,
                    "wallet2": sender1,
                    "asset1_number": amount1,
                    "asset2_number": 0,
                    "additional_data": {}
                }
                if callparams['function_caller'][0]['wallet_address'] == sender1:
                    trxn.append(tansaction_creator.transaction_type_5(transfer_proposal_data))

                    sc_state_proposal1_data = {
                        "operation": "update",
                        "table_name": "proposal_data",
                        "sc_address": self.address,
                        "data": {
                            "status": "disbursed    ",
                        },
                        "unique_column": "proposal_id",
                        "unique_value": qparam["proposal_id"]
                    }
                    trxn.append(tansaction_creator.transaction_type_8(sc_state_proposal1_data))

        return trxn

    def payout(self,callparamsip,repo:FetchRepository):
        # dividend to the members
        trxn=[]
        transaction_creator=TransactionCreator()
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        dao_id = self.address
        asset1_code=callparams['asset_code']
        amount=callparams['asset_amount']
        token_code = cspecs['token_name']
        members=repo.select_Query("wallet_address,balance").add_table_name("balances").where_clause("tokencode",token_code,4).execute_query_multiple_result({"tokencode":token_code})
        # members=cur.execute(f'''select wallet_address as owner,balance as amount from balances where tokencode like ?''',[token_code]).fetchall()
        locked_tokens=repo.select_Query("wallet_address,amount_locked").add_table_name("DAO_TOKEN_LOCK").where_clause("dao_id",dao_id,4).execute_query_multiple_result({"dao_id":dao_id})
        # locked_tokens=cur.execute(f'''select wallet_address as owner,amount_locked as amount from DAO_TOKEN_LOCK where dao_id like ?''',[dao_id]).fetchall()
        total_tokens=0
        qparam={"wallet_address":self.address,
                "tokencode":asset1_code}
        validationBalance=repo.select_Query("balance").add_table_name("balances").where_clause("wallet_address",qparam['wallet_address'],1).and_clause("tokencode",qparam['tokencode'],1).execute_query_single_result()
        if validationBalance is None or amount>validationBalance[0]:
            logger.log("Inadequate balance in SC for the tokeCode"+asset1_code)
            return []
        if members is not None:
            for i in members:
                total_tokens=total_tokens+i[1]
        ratio=int(amount)/int(total_tokens)
        for i in members:
            if(dao_id!=i[0]):
                transfer_proposal_data = {
                    "transfer_type": 1,
                    "asset1_code": asset1_code,
                    "asset2_code": "",
                    "wallet1": self.address,
                    "wallet2": i[0],
                    "asset1_number": math.floor(i[1]*ratio),
                    "asset2_number": 0,
                    "additional_data": {}
                }
                trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
                # transfer_tokens_and_update_balances(cur,dao_id,i[0],asset1_code,math.ceil(i[1]*ratio))
        for i in locked_tokens:
            if (dao_id != i[0]):
                transfer_proposal_data = {
                    "transfer_type": 1,
                    "asset1_code": asset1_code,
                    "asset2_code": "",
                    "wallet1": self.address,
                    "wallet2": i[0],
                    "asset1_number": math.floor(i[1] * ratio),
                    "asset2_number": 0,
                    "additional_data": {}
                }
                trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
                # transfer_tokens_and_update_balances(cur, dao_id, i[0], asset1_code, math.ceil(i[1] * ratio))
        return trxn
