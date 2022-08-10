from app.codes.kycwallet import create_add_wallet_transaction
from app.codes.tokenmanager import create_token_transaction
from app.codes.transactionmanager import Transactionmanager
from app.codes.transfermanager import Transfermanager
from app.routers.request_models import CreateTokenRequest, CreateWalletRequest


class TransactionCreator:
    def transaction_type_one(self, data: dict):
        add_wallet_request = {
            "custodian_wallet": data['custodian_wallet'],
            "ownertype": data['ownertype'],
            "jurisd": data['jurisdiction'],
            "kyc_docs": data['kyc_docs'],
            "specific_data": data['specific_data'],
            'wallet_address': data['address'],
            'wallet_public': data['public']
        }

        return create_add_wallet_transaction(add_wallet_request)

    def transaction_type_one_modal(self, data: CreateWalletRequest, wallet):
        add_wallet_request = {
            "custodian_address": data.custodian_address,
            "ownertype": data.ownertype,
            "jurisdiction": data.jurisdiction,
            "kyc_docs": data.kyc_docs,
            "specific_data": data.specific_data,
            "public_key": wallet['public']
        }
        return add_wallet_request

    def transaction_type_two(self, data: dict):
        add_token_request = {
            "tokenname": data['tokenname'],
            "tokencode": data['tokencode'],
            "tokentype": data.get('tokentype', 1),
            "first_owner": data['first_owner'],
            "custodian": data['custodian'],
            "disallowed": data.get('disallowed', {}),
            "legaldochash": data.get('legaldochash'),
            "amount_created": data.get('amount_created', 0),
            "tokendecimal": data.get('tokendecimal', 0),
            "disallowed_origin": data.get('disallowed_origin', []),
            "sc_flag": data.get('sc_flag', False),
            "tokenattributes": data.get('tokenattributes', {})
        }
        fulltrandata = {
            "transaction": {
                "timestamp": "",
                "trans_code": "000000",
                "type": 2,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": "",
                "valid": 1,
                "block_index": 0,
                "specific_data": add_token_request
            },
            "signatures": []
        }
        newtx = Transactionmanager()
        newtx.transactioncreator(fulltrandata)
        return newtx
        # return create_token_transaction(add_token_request)

    def transaction_type_3(self, data: dict):
        txspecdata = {
            "address": data['address'],
            "function": data['function'],
            "signers": data['signers'],
            "params": data['params']
        }
        fulltrandata = {
            "transaction": {
                "timestamp": "",
                "trans_code": "000000",
                "type": 3,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": "",
                "valid": 1,
                "block_index": 0,
                "specific_data": txspecdata
            },
            "signatures": []
        }
        newtx = Transactionmanager()
        newtx.transactioncreator(fulltrandata)
        return newtx

    def transaction_type_5(self, data: dict):
        trandata = {
            "transfer_type": 5,
            "asset1_code": str(data['asset1_code']),
            "asset2_code": str(data.get('asset2_code', "")),
            "wallet1": data['wallet1'],
            "wallet2": data['wallet2'],
            "asset1_number": data['asset1_number'],
            "asset2_number": data.get('asset2_number', 0),
            "additional_data": data['additional_data']
        }
        fulltrandata = {
            "transaction": {
                "timestamp": "",
                "trans_code": "000000",
                "type": 5,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": data.get('description', ""),
                "valid": 1,
                "block_index": 0,
                "specific_data": trandata
            },
            "signatures": []
        }
        newtx = Transactionmanager()
        newtx.transactioncreator(fulltrandata)
        return newtx

    def transaction_type_6(self, data: dict):
        txspecdata = {
            "address1": data['source_address'],
            "address2": data['destination_address'],
            "new_score": data['tscore'],
        }

        fulltrandata = {
            "transaction": {
                "timestamp": "",
                "trans_code": "000000",
                "type": 6,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": "",
                "valid": 1,
                "block_index": 0,
                "specific_data": txspecdata
            },
            "signatures": []
        }
        newtx = Transactionmanager()
        tdatanew = newtx.transactioncreator(fulltrandata)
        return tdatanew

    def transaction_type_8(self, data: dict):
        txspecdata = {
            "table_name": data['table_name'],
            "operation": data['operation'],
            "data": data.get('data',""),
            "address": data["sc_address"],
            "unique_column": data.get("unique_column",""),
            "unique_value": data.get("unique_value","")
        }

        fulltrandata = {
            "transaction": {
                "timestamp": "",
                "trans_code": "000000",
                "type": 8,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": "",
                "valid": 1,
                "block_index": 0,
                "specific_data": txspecdata
            },
            "signatures": []
        }
        newtx = Transactionmanager()
        newtx.transactioncreator(fulltrandata)
        return newtx
