

import math
from re import T
from app.codes.db_updater import input_to_dict
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from app.nvalues import STAKE_CT_ADDRESS, ZERO_ADDRESS
from .contract_master import ContractMaster


class og_stake(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "og_stake"
        self.version = ""
        ContractMaster.__init__(self, self.template,
                                self.version, contractaddress)
    


    def stake(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        # TODO check for self balance
        callparams = input_to_dict(callparamsip)
        token_code = cspecs['issuance_token_code']
        token_multiplier = cspecs['token_multiplier']
        value = callparams['value']
        wallet_address = callparams['wallet_address']
        amount_to_issue = value[0]['amount']
        amount_to_stake = amount_to_issue * token_multiplier
        required_value = {
            "token_code": token_code,
            "amount": amount_to_issue
        }

        if required_value in value:
            transaction_creator = TransactionCreator()
            params = {
                "token_amount":amount_to_stake,
                "wallet_address": wallet_address,
                "value": [
                    {
                        "token_code": "NWRL",
                        "amount": amount_to_stake,
                    }
                ]
            }
            txspecdata = {
                "address": STAKE_CT_ADDRESS,
                "function": 'stake_tokens',
                "signers": [self.address],
                "params": params,
            }
            sc_transaction = transaction_creator.transaction_type_3(txspecdata)
            return [sc_transaction]


    def unstake(self, callparamsip, repo: FetchRepository):
        
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        # TODO check for self balance
        callparams = input_to_dict(callparamsip)
        token_code = cspecs['issuance_token_code']
        token_multiplier = cspecs['token_multiplier']
        wallet_address = callparams['wallet_address']
        person_id = callparams['person_id']
        amount_to_unstake = callparams['og_unstake_amount']
        amount_to_stake = amount_to_unstake * token_multiplier
  

        transaction_creator = TransactionCreator()
        params = {
            "token_amount":amount_to_stake,
            "wallet_address": wallet_address,
            "person_id": person_id
        }
        txspecdata = {
            "address": STAKE_CT_ADDRESS,
            "function": 'unstake_tokens',
            "signers": [self.address],
            "params": params,
            "function_caller": self.address
        }
        sc_transaction = transaction_creator.transaction_type_3(txspecdata)
        return [sc_transaction]


    
    def remove(self, callparamsip, repo: FetchRepository):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)

        withdraw_address = cspecs['withdraw_address']
        amount = callparams['amount']
        issuer = cspecs['issuer']

        function_caller = callparams['function_caller'][0]['wallet_address']

        if issuer != function_caller:
            raise Exception("Caller is not authorized")

        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
                "transfer_type": 1,
                "asset1_code": "NWRL",
                "asset2_code": "",
                "wallet1": self.address,
                "wallet2": withdraw_address,
                "asset1_number": amount,
                "asset2_number": 0,
                "additional_data": {}
            }
        transfer_proposal = transaction_creator.transaction_type_5(
                transfer_proposal_data)

        return [transfer_proposal]