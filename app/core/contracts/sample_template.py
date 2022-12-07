from app.core.db.db_updater import input_to_dict
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator
from .contract_master import ContractMaster
from app.core.helpers.CustomExceptions import ContractValidationError


class sample_template(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, address=None):
        self.template = "sample_template"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, address)

    def value_issue(self, params, fetchRepository: FetchRepository):
        '''
        Sample Method which validates value which is to be sent as part of txn and issues tokens
        '''

        child_transactions = []

        amount_to_issue = params['amount_to_issue']
        address_to_issue = params['address_to_issue']
        token_code = 'sample_template_token'
        token_name = token_code

        value = params["value"]
        #assuming amount to be issued to equal to value
        required_value = {
            "token_code": "NWRL",
            "amount": amount_to_issue
        }

        if required_value in value:
            transaction_creator = TransactionCreator()
            tokendata = {
                "tokenname": token_name,
                "tokencode": token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": address_to_issue,
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": amount_to_issue,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            child_transactions.append(
                transaction_creator.transaction_type_two(tokendata))

        return child_transactions

    def create_entry(self, params, fetFetchRepository: FetchRepository):
        '''
        Sample method to create a new state data entry
        This method maps wallet address to a name
        '''

        name = params['name']
        wallet_address = params['wallet_address']

        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update) sample proposal'''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": self.template,
            "sc_address": self.address,
            "data": {
                "address": self.address, #address (which is a key to idenetify rows of this contract) should be auto populated from sc_address?
                "wallet_address": wallet_address,
                "name": name
            }
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [sc_state_proposal1]

    def update_entry(self, params, fetFetchRepository: FetchRepository):
        '''
        Sample method to update a state data entry
        This method maps wallet address to a name
        '''
        wallet_address = params['wallet_address']
        name = params['name']

        transaction_creator = TransactionCreator()
        '''txn type 8 (sc-private state update) sample proposal'''
        sc_state_proposal1_data = {
            "operation": "update",
            "table_name": self.template,
            "sc_address": self.address,
            "unique_column":"wallet_address",
            "unique_value": wallet_address,
            "data": {
                "address": self.address,
                "name": name
            }
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [sc_state_proposal1]


    def transfer_and_update(self, params, fetFetchRepository: FetchRepository):
        '''
        EXAMPLE METHOD THAT HAS SAMPLE CHILD TXNS 
        '''

        '''txn type 5 (one way transfer) sample proposal'''
        transaction_creator = TransactionCreator()
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": "NWRL",
            "asset2_code": "",
            "wallet1": self.address,
            "wallet2": "0x20513a419d5b11cd510ae518dc04ac1690afbed6",
            "asset1_number": 1,
            "asset2_number": 0,
            "additional_data": {}
        }
        transfer_proposal = transaction_creator.transaction_type_5(
            transfer_proposal_data)

        '''txn type 8 (sc-private state update) sample proposal'''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": "sc_test",
            "sc_address": self.address,
            "data": {
                "address": "0x75ff59811ba2df3c9b76d02bb156dd4a29a0dff8",
                "total_transfer_amount": 1
            }
        }
        sc_state_proposal1 = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        '''txn type 3 (sc call) sample proposal'''
        sc_proposal1_params = {
            "recipient_address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6",
            "amount": 2,
            "tokencode": "MEME_TOKEN_DAO_token"
        }
        sc_proposal1_data = {
            "address": "cte9bf57899687d0e732e7ff895aefa57e6525de35",
            "function": 'issue_token',
            "signers": [self.address],
            "params": sc_proposal1_params
        }
        sc_proposal1 = transaction_creator.transaction_type_3(
            sc_proposal1_data)
        return [sc_proposal1]

    def sample_validate(self, params, fetFetchRepository: FetchRepository):
        print("Sample_validate invoked")
        return []

    def validate(self, txn_data, fetFetchRepository: FetchRepository):
        method = txn_data["function"]
        if(method == "sample_validate"):
            value = txn_data["params"]["value"]
            token_1 = value[0]
            token_1_code = token_1["token_code"]
            if token_1_code != "OT1":
                raise ContractValidationError("Provided value tokens are incorrect, please provide ot1 tokens only")
        pass
                            
