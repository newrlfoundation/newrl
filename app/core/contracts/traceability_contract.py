from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
from app.core.helpers.utils import get_last_block_hash
from .contract_master import ContractMaster
from app.core.helpers.CustomExceptions import ContractValidationError


class traceability_contract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, address=None):
        self.template = "traceability_contract"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, address)


    def submit_token(self, callparamsip, fetFetchRepository: FetchRepository):
        callparams = input_to_dict(callparamsip)


        recipient = callparams['recipient']
        child_token_type = callparams['child_token_type']
        initiator_wallet = callparams['function_caller'][0]['wallet_address']
        ratio = callparams['ratio']
        diff = callparams['diff']

        value = callparams['value']

        if value is None or len(value) == 0:
            raise Exception("Incorrect value provided")
        
        amount = value[0]["amount"]
        parent_token_code = value[0]["token_code"]

        #TODO check wallet
        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update) '''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": self.template,
            "sc_address": self.address,
            "data": {
                "address": self.address, #address (which is a key to idenetify rows of this contract) should be auto populated from sc_address?
                "initiator_wallet": initiator_wallet,
                "init_timestamp": get_last_block_hash()["timestamp"],
                "status":"initialized",
                "parent_token_code":parent_token_code,
                "parent_token_transaction":"",
                "claimer_wallet":recipient,
                "claim_timesteamp":"",
                "child_token_code":"",
                "child_token_type":child_token_type,
                "amount":amount,
                "ratio":ratio,
                "diff":diff,
            }
        }
        
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [sc_state_proposal1]

    def claim_token(self, callparamsip, fetFetchRepository: FetchRepository):
        callparams = input_to_dict(callparamsip)

        child_token_attributes = callparamsip['child_token_attributes']
        child_token_code = callparamsip['child_token_code']
        child_token_name = callparamsip['child_token_name']
        parent_token_code = callparamsip['parent_token_code']
        initiator_wallet = callparamsip['initiator_wallet']
        claimer_wallet = callparams['function_caller'][0]['wallet_address']

        existing_state = self._fetch_state(self,parent_token_code, initiator_wallet,fetFetchRepository)
        #todo validation of existing state

        #type 2 to create token
        transaction_creator = TransactionCreator()
        tokendata = {
            "tokenname": child_token_name,
            "tokencode": child_token_code,
            "tokentype": '1',
            "tokenattributes": child_token_attributes,
            "first_owner": claimer_wallet,
            "custodian": self.address,
            "legaldochash": '',
            "amount_created": 1,
            "value_created": '',
            "disallowed": {},
            "sc_flag": True,
        }
        token_creation = transaction_creator.transaction_type_two(tokendata)

        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update) '''
        data = {
                "address": self.address, #address (which is a key to idenetify rows of this contract) should be auto populated from sc_address?
                "initiator_wallet": initiator_wallet,
                "init_timestamp": existing_state[2],
                "status":"claimed",
                "parent_token_code":parent_token_code,
                "parent_token_transaction":"",
                "claimer_wallet":claimer_wallet,
                "claim_timesteamp":get_last_block_hash()["timestamp"],
                "child_token_code":child_token_code,
                "child_token_type":"",
                "amount":existing_state[10],
                "ratio":existing_state[11],
                "diff":existing_state[12],
            }
        sc_state_proposal1_data = {
            "operation": "update",
            "table_name": self.template,
            "sc_address": self.address,
            "unique_column":"parent_token_code",
            "unique_value": parent_token_code,
            "data": data
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [token_creation,sc_state_proposal1]

    def _fetch_state(self, alias, token_code, initiator_wallet, repo:FetchRepository):
        state = repo.select_Query().add_table_name(self.template).where_clause("parent_token_code", token_code, 1).and_clause(
                    "initiator_wallet", initiator_wallet, 1).execute_query_multiple_result({"parent_token_code": token_code,"initiator_wallet":initiator_wallet})
        if len(state) == 0:
                raise Exception("Alias does not exist to modify/update")
        return state[0]

    # def validate(self, txn_data, fetFetchRepository: FetchRepository):
    #     method = txn_data["function"]
    #     if(method == "sample_validate"):
    #         value = txn_data["params"]["value"]
    #         token_1 = value[0]
    #         token_1_code = token_1["token_code"]
    #         if token_1_code != "OT1":
    #             raise ContractValidationError("Provided value tokens are incorrect, please provide ot1 tokens only")
    #     pass
                            
