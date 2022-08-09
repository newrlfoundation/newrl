import json
import sqlite3

from app.codes.transactionmanager import Transactionmanager
from app.constants import NEWRL_DB
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
        if not 'is_type_value' in transaction.transaction['specific_data']['additional_data']:
            if contract_address != transaction.transaction['specific_data']['wallet1']:
                return False
    if type==TRANSACTION_TRUST_SCORE_CHANGE:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        signatories = cur.execute(
            'SELECT signatories FROM contracts WHERE address=?', (contract_address,)).fetchone()
        con.close()
        if signatories is None:
            print("Contract does not exist.")
            return [-1]
        functsignmap = json.loads(signatories[0])
        add1_exist=False
        add2_exist=False
        if transaction.transaction['specific_data']['address1'] in functsignmap.get('update_trust_score',[]):
            add1_exist=True
        if transaction.transaction['specific_data']['address2'] in functsignmap('update_trust_score',[]):
            add2_exist=False
        return (add1_exist and add2_exist)


    if type == TRANSACTION_MINER_ADDITION:
        return False
    if type == TRANSACTION_SC_UPDATE:
        if transaction.transaction['specific_data']['sc_address'] != contract_address:
            return False   
    if type != TRANSACTION_SC_UPDATE:
        return transaction.econvalidator()
    
    return True