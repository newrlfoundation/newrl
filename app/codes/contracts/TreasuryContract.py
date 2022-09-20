# class to stake token from user
import math

from .contract_master import ContractMaster
from ..clock.global_time import get_corrected_time_ms
from ..db_updater import *
from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator
import logging

from ...nvalues import STAKE_COOLDOWN_MS, ASQI_WALLET, FOUNDATION_WALLET, ZERO_ADDRESS
# NETWORK should habve
# TODO : Add emerbship check remove hardcode have more than n/2 +1 Newrl Foundation
class TreasuryContract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, contractaddress=None):
        self.template = "TreasuryContract"
        self.version = "1.0.0"
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def burn_token(self,callparamsip,repo:FetchRepository):
        callparams=input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        dao_address = cspecs['dao_address']
        function_caller = callparams['function_caller']
        wallet_present = True
        membership_wallets = []
        person_ids = self.get_members_from_dao(dao_address, membership_wallets, repo)
        for i in function_caller:
            if i['wallet_address'] not in membership_wallets[0]:
                if person_ids is not None and get_person_id_for_wallet_address(i['wallet_address']) not in person_ids:
                    wallet_present = False

        if wallet_present:
            amount=callparams['amount']
            transaction_creator=TransactionCreator()
            transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": 'NWRL',
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": ZERO_ADDRESS,
                "asset1_number": int(amount),
                "asset2_number": 0,
                "additional_data": {}
            }
            trxn = transaction_creator.transaction_type_5(transfer_proposal_data)
            return [trxn]
        else:
            return []

    def upgrade_transfer(self,callparamsip,repo:FetchRepository):
        trxn=[]
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        dao_address = cspecs['dao_address']
        function_caller = callparams['function_caller']
        wallet_present = True
        membership_wallets = []
        person_ids = self.get_members_from_dao(dao_address, membership_wallets, repo)
        for i in function_caller:
            if i['wallet_address'] not in membership_wallets[0]:
                if person_ids is not None and get_person_id_for_wallet_address(i['wallet_address']) not in person_ids:
                    wallet_present = False


        if wallet_present:

            new_ct_address=callparams['ct_address']
            count=repo.select_count().add_table_name('contracts').where_clause('address',new_ct_address,1).and_clause('status',1,1).execute_query_single_result({"address":new_ct_address,"status":1})
            if count is None:
                self.logger.info("No such contract found")
                return []
            else:
                balancesTuple=repo.select_Query('token_code,balance').add_table_name('balances').where_clause('wallet_address',self.address,1).execute_query_multiple_result({"wallet_address":self.address})
                if balancesTuple is not None:
                    for i in balancesTuple:
                        transaction_creator=TransactionCreator()
                        transfer_proposal_data = {
                            "transfer_type": 1,
                            "asset1_code": i[0],
                            "asset2_code": "",
                            "wallet1": self.address,
                            "wallet2": new_ct_address,
                            "asset1_number": float(i[1]),
                            "asset2_number": 0,
                            "additional_data": {}
                        }
                        trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
                return trxn
        else:
            return []

    def payout(self,callparamsip,repo:FetchRepository):
        trxn = []
        total_tokens=0
        callparams=input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        dao_address = cspecs['dao_address']
        function_caller = callparams['function_caller']
        wallet_present = True
        membership_wallets = []
        person_ids = self.get_members_from_dao(dao_address, membership_wallets, repo)
        for i in function_caller:
            if i['wallet_address'] not in membership_wallets[0]:
                if person_ids is not None and get_person_id_for_wallet_address(i['wallet_address']) not in person_ids:
                    wallet_present = False
        if wallet_present:
            user_defined_ratio=callparams.get('amount',100)
            # SC address to be excluded from the query
            balancesTuple = repo.select_Query('wallet_address,balance').add_table_name('balances').where_clause(
                'token_code','NWRL', 1).and_clause('wallet_address',self.address,5).execute_query_multiple_result({"token_code": 'NWRL','wallet_address':self.address})
            contract_balance=repo.select_Query('tokencode,balance').add_table_name('balances').where_clause('wallet_address',self.address,1).execute_query_multiple_result({"wallet_address":self.address})
            if contract_balance is None:
                return []
            if balancesTuple is None:
                return []
            else:
                size=len(balancesTuple)
                for i in balancesTuple:
                    total_tokens=total_tokens+int(i[1])
                ratio=total_tokens/size
                for i in balancesTuple:
                    for j in contract_balance:
                        amount_to_send=math.floor(j[1]*i[1]*ratio*(user_defined_ratio/100))
                        reciever=i[0]
                        transfer_proposal_data = {
                            "transfer_type": 1,
                            "asset1_code": j[0],
                            "asset2_code": "",
                            "wallet1": self.address,
                            "wallet2": reciever,
                            "asset1_number": amount_to_send,
                            "asset2_number": 0,
                            "additional_data": {}
                        }
                        transaction_creator=TransactionCreator()
                        trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))


            return trxn
        else:
            return []

    def transfer(self,callparamsip,repo:FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        dao_address = cspecs['dao_address']
        function_caller = callparams['function_caller']
        wallet_addresses = []
        for i in function_caller:
            wallet_addresses.append(i['wallet_address'])
        wallet_addresses = set(wallet_addresses)
        number_of_sign = len(wallet_addresses)
        transfer_limits = json.loads(cspecs['transfer_limits'])
        transfer_limit = transfer_limits[number_of_sign]
        wallet_present = True
        membership_wallets = []
        wallet_to_send = callparams['receiver']
        amount_to_send = callparams['amount_to_send']
        asset_code = callparams.get('asset_code','NWRL')
        person_ids = self.get_members_from_dao(dao_address, membership_wallets, repo)
        for i in function_caller:
            if i['wallet_address'] not in membership_wallets[0]:
                if person_ids is not None and get_person_id_for_wallet_address(i['wallet_address']) not in person_ids:
                    wallet_present = False

        if wallet_present and amount_to_send <= transfer_limit:
            transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": asset_code,
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": wallet_to_send,
                "asset1_number": amount_to_send,
                "asset2_number": 0,
                "additional_data": {}
            }
            transaction_creator = TransactionCreator()
            trxn.append(transaction_creator.transaction_type_5(transfer_proposal_data))
        return trxn

    def get_members_from_dao(self, dao_address, membership_wallets, repo):
        query_param = {"dao_person_id": get_person_id_for_wallet_address(dao_address)}
        person_ids = repo.select_Query('member_person_id').add_table_name("dao_membership").where_clause("dao_person_id",
                                                                                                  query_param[
                                                                                                       "dao_person_id"],
                                                                                                  1).execute_query_multiple_result(
            query_param)
        membership_wallets.append(json.loads(Configuration.config("MEMBER_WALLET_LIST")))
        if person_ids is None:
            return []
        else:
            return person_ids
