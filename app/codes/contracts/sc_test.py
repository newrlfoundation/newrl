from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.helpers.TransactionCreator import TransactionCreator
from .contract_master import ContractMaster

class sc_test(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, address=None):
        self.template = "sc_test"
        self.version = ""
        ContractMaster.__init__(self, self.template,self.version, address)

    def transfer_and_update(self, params, fetFetchRepository : FetchRepository):
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
        transfer_proposal = transaction_creator.transaction_type_5(transfer_proposal_data)

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
        sc_state_proposal1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)


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
        sc_proposal1 = transaction_creator.transaction_type_3(sc_proposal1_data)
        return [sc_proposal1]

    def value_handle(self, params, fetFetchRepository: FetchRepository):
        '''
        Sample Method which validates value will be sent as part of txn and issues tokens
        '''

        child_transactions = []

        value = params["value"]

        required_value = {
            "token_code": "NWRL",
            "amount": 1
        }

        if required_value in value:
            transaction_creator = TransactionCreator()
            tokendata={
                "tokenname": 'token_code',
                "tokencode": 'token_code',
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": "0x20513a419d5b11cd510ae518dc04ac1690afbed6",
                "custodian": self.address,
                "legaldochash": '',
                "amount_created": 2,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            child_transactions.append(
                transaction_creator.transaction_type_two(tokendata))

        return child_transactions
