from .dao_main_template import DaoMainTemplate
from ..db_updater import *
import math

class token_fund_dao(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None):
        self.template= 'token_fund_dao'
        self.version='1.0.0'
        self.dao_type=2
        # dao_type=2 is for token based DAO and 1 is for membership DAO
        super().__init__(contractaddress)

    def invest(self,cur,callparamsip):
        # Invest in any startup
        callparams = input_to_dict(callparamsip)
        dao_id = self.address
        wallet_to_invest=callparams['wallet_to_invest']
        token_to_invest_code=callparams['invest_token_code']
        token_to_invest_amount = callparams['invest_token_amount']
        token_to_recieve=callparams['token_to_recieve']
        token_recieve_amt = callparams['token_recieve_amt']
        # Transfering Tokens from User To DAO
        sender1 = wallet_to_invest
        sender2 = dao_id

        tokencode1 = token_to_invest_code
        amount1 = int(token_to_invest_amount or 0)
        transfer_tokens_and_update_balances(
            cur, sender2, sender1, tokencode1, amount1)

        tokencode2 = token_to_recieve
        amount2 = int(token_recieve_amt or 0)
        transfer_tokens_and_update_balances(
            cur, sender1, sender2, tokencode2, amount2)

        pass

    def disburse(self,cur,callsparamip):
        # function to send money to the startup

        pass

    def payout(self,cur,callparamsip):
        # dividend to the members
        callparams = input_to_dict(callparamsip)
        dao_id = self.address
        asset1_code=callparams['asset_code']
        amount=callparams['asset_amount']
        dao_data=cur.execute(f'''Select dao_name as dao_name from dao_main where dao_sc_address=?''',[self.address])
        dao_data=dao_data.fetchone()
        token_code = dao_data[0]+'_token'
        members=cur.execute(f'''select wallet_address as owner,balance as amount from balances where tokencode like ?''',[token_code]).fetchall()
        locked_tokens=cur.execute(f'''select wallet_address as owner,amount_locked as amount from DAO_TOKEN_LOCK where dao_id like ?''',[dao_id]).fetchall()
        total_tokens=0
        if members is not None:
            for i in members:
                total_tokens=total_tokens+i[1]
        ratio=int(amount)/int(total_tokens)
        for i in members:
            if(dao_id!=i[0]):
                transfer_tokens_and_update_balances(cur,dao_id,i[0],asset1_code,math.ceil(i[1]*ratio))
        for i in locked_tokens:
            if (dao_id != i[0]):
                transfer_tokens_and_update_balances(cur, dao_id, i[0], asset1_code, math.ceil(i[1] * ratio))
        pass
