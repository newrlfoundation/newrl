from app.codes.kycwallet import create_add_wallet_transaction
from app.codes.tokenmanager import create_token_transaction
from app.codes.transactionmanager import Transactionmanager
from app.codes.transfermanager import Transfermanager
from app.routers.request_models import CreateTokenRequest, CreateWalletRequest


class TransactionCreator:
    def transaction_type_one(self,data:dict):

        add_wallet_request = {
            "custodian_address": data['custodian_address'],
            "ownertype": data['ownertype'],
            "jurisd ": data['jurisdiction'],
            "kyc_docs": data['kyc_docs'],
            "specific_data": data['specific_data'],
            'wallet_address': data['address'],
            'wallet_public': data['public']
        }

        return create_add_wallet_transaction(add_wallet_request)
    def transaction_type_one_modal(self,data:CreateWalletRequest,wallet):
        add_wallet_request = {
            "custodian_address": data.custodian_address,
            "ownertype": data.ownertype,
            "jurisdiction": data.jurisdiction,
            "kyc_docs": data.kyc_docs,
            "specific_data": data.specific_data,
            "public_key": wallet['public']
        }
        return add_wallet_request
    def transaction_type_two(self,data:dict):
        add_token_request = {
            "token_name": data['token_name'],
            "token_code": data['token_code'],
            "token_type": data.get('token_type',1),
            "first_owner": data['first_owner'],
            "custodian": data['custodian_address'],
            "legal_doc": data.get('legal_docs',{}),
            "amount_created": data.get('amount',0),
            "tokendecimal": data.get('token_decimal',0),
            "disallowed_regions": data.get('disallowed_origin',[]),
            "is_smart_contract_token": data.get('is_sc_token',False),
            "token_attributes": data.get('token_attributes',{})
        }
        return create_token_transaction(add_token_request)
    def transaction_type_two_modal(self,data:CreateTokenRequest):
        add_token_request = {
            "token_name": data.token_name,
            "token_code": data.token_code,
            "token_type": data.token_type,
            "first_owner": data.first_owner,
            "custodian": data.custodian,
            "legal_doc": data.legal_doc,
            "amount_created": data.amount_created,
            "tokendecimal": data.tokendecimal,
            "disallowed_regions": data.disallowed_regions,
            "is_smart_contract_token": data.is_smart_contract_token,
            "token_attributes": data.token_attributes
        }
        return add_token_request

    def transaction_type_5(self,data:dict):
        trandata = {
            "transfer_type": 5,
            "asset1_code": str(data['asset1_code']),
            "asset2_code": str(data.get('asset2_code',"")),
            "wallet1": data['wallet1_address'],
            "wallet2": data['wallet2_address'],
            "asset1_number": data['asset1_qty'],
            "asset2_number": data.get('asset2_qty',""),
            "additional_data": data['additional_data']
        }
        fulltrandata = {
            "transaction": {
                "timestamp": "",
                "trans_code": "000000",
                "type": type,
                "currency": "NWRL",
                "fee": 0.0,
                "descr": data.get('description',""),
                "valid": 1,
                "block_index": 0,
                "specific_data": trandata
            },
            "signatures": []
        }
        newtransfer = Transfermanager(transfer_data=fulltrandata)
        tdatanew = newtransfer.loadandcreate()
        return tdatanew

    def transaction_type_6(self,data:dict):
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