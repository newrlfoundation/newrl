# class to create smart contract for creating stablecoins on Newrl
import base64

from ecdsa import BadSignatureError

from .contract_master import ContractMaster
from ..db_updater import *
from ..transactionmanager import get_public_key_from_address, Transactionmanager


class CarbonCredits(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "AuthorizeContract"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def validateCustodian(self, transaction, custodian_address, custodian_wallet, transaction_manager):
        valid = False
        matchedCustodian = [x for x in transaction['signatures'] if x['wallet_address'] == custodian_address][0]
        if (matchedCustodian is not None):
            try:
                sign_valid = transaction_manager.verify_sign(matchedCustodian['msgsign'],
                                                             custodian_wallet)
                valid = sign_valid
            except BadSignatureError:
                valid = False
            finally:
                return valid
        else:
            return False

    def validate(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        custodian_address = cspecs['custodian_address']
        custodian_wallet = base64.b64decode(get_public_key_from_address(custodian_address))

        transaction_manager = Transactionmanager()
        transaction_manager.set_transaction_data(callparams)

        return self.validateCustodian(callparams, custodian_address, custodian_wallet, transaction_manager)

    def assignScores(self, cur, callparamsip):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        minScoreCount = cspecs['minScoreCount']
        reportData = cspecs['reportData']
        currentScores = cspecs['currentScores']
        if self.validate(cur, callparamsip):
            callparams = input_to_dict(callparamsip)
            serverID = callparams['transaction']['serverID']
            score = callparams['transaction']['score']
            currentScores.append(
                {
                    "serverID": serverID,
                    "score": score
                }
            )
            ###updateContract params here
            # if len(currentScores) >= minScoreCount:
            #     for score in currentScores:
            #         return
        else:
            return "Invalid Transaction: Error in custodian signature"
