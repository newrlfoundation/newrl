# class to create smart contract for creating stablecoins on Newrl
import base64

from ecdsa import BadSignatureError

from .contract_master import ContractMaster
from ..db_updater import *
from ..helpers.FetchRespository import FetchRepository
from ..helpers.TransactionCreator import TransactionCreator
from ..transactionmanager import get_public_key_from_address, Transactionmanager


class AuthorizeContract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "AuthorizeContract"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def validateCustodian(self, transaction, custodian_address, custodian_wallet, transaction_manager):
        valid = False
        matchedCustodian = [x for x in transaction["transaction"]['signatures'] if x['wallet_address'] == custodian_address]
        if (matchedCustodian is not None):
            try:
                sign_valid = transaction_manager.verify_sign(matchedCustodian[0]['msgsign'],
                                                             custodian_wallet)
                valid = sign_valid
            except BadSignatureError:
                valid = False
            finally:
                return valid
        else:
            return False

    def _validate(self, callparamsip, repo: FetchRepository):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        custodian_address = cspecs['custodian_address']
        custodian_wallet = bytes.fromhex(get_public_key_from_address(custodian_address))

        transaction_manager = Transactionmanager()
        transaction_manager.set_transaction_data(callparams["transaction"])

        return self.validateCustodian(callparams, custodian_address, custodian_wallet, transaction_manager)

    def modifyTokenAttributes(self, callparamsip, repo: FetchRepository):
        if self._validate(callparamsip, repo):

            transaction_creator = TransactionCreator()
            trxn = []
            callparams = input_to_dict(callparamsip)
            query_params = (
                callparams['transaction']['transaction']['token_code'],
                callparams['transaction']['transaction']['timestamp'],
                callparams['transaction']['transaction']['token_attributes'],

            )
            # cursor = cur.execute('SELECT token_attributes FROM tokens WHERE tokencode = :tokencode',
            #                      {'tokencode': query_params[0]})
            # tokenAttributes = cursor.fetchone()
            tokenAttributes = repo.select_Query("token_attributes"). \
                add_table_name("tokens").where_clause("tokencode", query_params[0], 1). \
                execute_query_single_result({'tokencode': query_params[0]})
            jsonObj = json.loads(tokenAttributes[0])
            list = []
            if "append" in jsonObj:
                list = jsonObj["append"]
            list.append({query_params[1]: query_params[2]})
            jsonObj["append"] = list
            attributes = json.dumps(jsonObj)
            # cur.execute(f'''UPDATE tokens SET token_attributes= :attr WHERE tokenCode= :code''',
            #             {'attr': attributes,
            #              'code': query_params[0]})
            sc_state_proposal1_data = {
                "operation": "update",
                "table_name": "tokens",
                "sc_address": self.address,
                "data": {
                    "token_attributes": attributes
                },
                "unique_column": "tokenCode",
                "unique_value": query_params[0]
            }
            trxn.append(transaction_creator.transaction_type_8(sc_state_proposal1_data))
            logger.info("Modification transaction successful %s" % query_params[0])
            return trxn
        else:
            return "Invalid Transaction: Error in custodian signature"

    def destroyTokens(self,callparamsip ,repo: FetchRepository):
        trxns=[]
        callparams=input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        custodian_address = cspecs['custodian_address']
        function_caller = callparams['function_caller']
        for i in function_caller:
            if i["wallet_address"] == custodian_address:
                return trxns
        raise ("Custodian didn signed the txn")

    def burnToken(self,callparamsip,repo: FetchRepository):
        trxns = []
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        custodian_address = cspecs['custodian_address']
        function_caller = callparams['function_caller']
        wallet_present = False
        for i in function_caller:
            if i["wallet_address"] == custodian_address:
                wallet_present = True
                break;
        if not wallet_present:
            raise ("Custodian didnt signed the txn")
        qparam = {
            "wallet_address":self.address,
            "balance":0
        }
        data = repo.select_Query("tokencode,balance").add_table_name("balances").where_clause("wallet_address",self.address,1).and_clause("balance",0,5).execute_query_multiple_result(qparam)
        if data is not None:
            for i in data:
                transaction_creator = TransactionCreator()
                transfer_proposal_data = {
                    "transfer_type": 5,
                    "asset1_code": i[0],
                    "asset2_code": "",
                    "wallet1": self.address,
                    "wallet2": Configuration.config("ZERO_ADDRESS"),
                    "asset1_number": int(i[1]),
                    "asset2_number": 0,
                    "additional_data": {}
                }
                trxn = transaction_creator.transaction_type_5(transfer_proposal_data)
                trxns.append(trxn)
        return trxns



    def createTokens(self, callparamsip, repo: FetchRepository):
        trxn = []
        callparams = input_to_dict(callparamsip)
        token_code = callparams['token_code']
        amount = callparams['token_amount']
        token_name = callparams.get('token_name', token_code)
        recipient_address = callparams['recipient_address']
        token_attributes = callparams.get('token_attributes', {})
        value_created = callparams.get('value_created', '')
        legal_doc = callparams.get('legal_doc', '')
        tokendata = {
            "tokenname": token_name,
            "tokencode": token_code,
            "tokentype": '31',
            "tokenattributes": token_attributes,
            "first_owner": recipient_address,
            "custodian": self.address,
            "legaldochash": legal_doc,
            "amount_created": amount,
            "value_created": value_created,
            "disallowed": {},
            "sc_flag": True
        }
        transacation_creator = TransactionCreator()
        trxn.append(transacation_creator.transaction_type_two(tokendata))
        return trxn

    def terminate(self, callparamsip, repo: FetchRepository):

        transaction_creator = TransactionCreator()
        trxn = []
        sc_state_proposal1_data = {
            "operation": "update",
            "table_name": "contracts",
            "sc_address": self.address,
            "data": {
                "status": -1
            },
            "unique_column": "address",
            "unique_value": self.address
        }
        trxn.append(transaction_creator.transaction_type_8(sc_state_proposal1_data))
        # cur.execute(f'''UPDATE contracts SET status=-1 WHERE address= :address''',
        #             {'address': self.address})
        logger.info("Contract delete successful %s" % self.address)
        return trxn
