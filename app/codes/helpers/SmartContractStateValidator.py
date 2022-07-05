from app.codes.transactionmanager import Transactionmanager
from app.ntypes import *


def validate(transaction: Transactionmanager, contract_address: str):
    type = transaction.transaction['type']
    if type == TRANSACTION_WALLET_CREATION:
        if transaction.transaction['specific_data']['custodian_wallet'] != contract_address:
            return False
    if type == TRANSACTION_TOKEN_CREATION:
        if transaction.transaction['specific_data']['custodian'] != contract_address:
            return False
    if type == TRANSACTION_SMART_CONTRACT:
        if contract_address not in transaction.transaction['specific_data']['signers']:
            return False
    if type == TRANSACTION_TWO_WAY_TRANSFER:
        return False
    if type == TRANSACTION_ONE_WAY_TRANSFER:
        if contract_address != transaction.transaction['specific_data']['wallet1']:
            return False
    # if type==TRANSACTION_TRUST_SCORE_CHANGE:
    #     #         TBD

    if type == TRANSACTION_MINER_ADDITION:
        return False
    if type == TRANSACTION_SC_UPDATE:
        if transaction.transaction['specific_data']['sc_address'] != contract_address:
            return False   
    if type != TRANSACTION_SC_UPDATE:
        return transaction.econvalidator()
    
    return True