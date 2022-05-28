# class to create smart contract for creating stablecoins on Newrl
import base64

from ecdsa import BadSignatureError

from .contract_master import ContractMaster
from ..db_updater import *
from ..transactionmanager import get_public_key_from_address, Transactionmanager


class AuthorizeContract(ContractMaster):
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

    def modifyTokenAttributes(self, cur, callparamsip):
        if self.validate(cur, callparamsip):
            callparams = input_to_dict(callparamsip)
            query_params = (
                callparams['transaction']['token_code'],
                callparams['transaction']['timestamp'],
                callparams['transaction']['token_attributes'],

            )
            cursor = cur.execute('SELECT token_attributes FROM tokens WHERE tokencode = :tokencode',
                                 {'tokencode': query_params[0]})
            tokenAttributes = cursor.fetchone()
            jsonObj = json.loads(tokenAttributes[0])
            list = []
            if "append" in jsonObj:
                list = jsonObj["append"]
            list.append({query_params[1]: query_params[2]})
            jsonObj["append"] = list
            attributes = json.dumps(jsonObj)
            cur.execute(f'''UPDATE tokens SET token_attributes= :attr WHERE tokenCode= :code''',
                        {'attr': attributes,
                         'code': query_params[0]})
            return "Modification transaction successful %s" % query_params[0]
        else:
            return "Invalid Transaction: Error in custodian signature"

    def destroyTokens(self, cur, callparamsip):
        pass

    def createTokens(self, cur, callparamsip):
        pass

    def terminate(self, cur, callparamsip):
        cur.execute(f'''UPDATE contracts SET status=-1 WHERE address= :address''',
                    {'address': self.address})
        return "Contract delete successful %s" % self.address
