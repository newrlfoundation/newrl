import logging
import math
import json
import importlib
from lib2to3.pgen2 import token
import re
import traceback
from app.core.auth.auth import get_wallet
from app.core.helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator

from .transactionmanager import Transactionmanager, get_valid_addresses
from ..helpers.SmartContractStateValidator import validate
from app.core.clock.global_time import get_corrected_time_ms
from app.core.helpers.CentralRespository import CentralRepository
from ..db.db_updater import *
from app.core.consensus.networkscoremanager import get_invalid_block_creation_score, get_invalid_receipt_score, get_valid_block_creation_score, get_valid_receipt_score, update_network_trust_score_from_receipt
from ..p2p.utils import get_peers
from app.config.Configuration import Configuration

from app.config.nvalues import NETWORK_TRUST_MANAGER_PID, TREASURY_WALLET_ADDRESS

from app.config.nvalues import NETWORK_TRUST_MANAGER_PID, MIN_STAKE_AMOUNT, STAKE_PENALTY_RATIO, ZERO_ADDRESS

from app.config.constants import ALLOWED_FEE_PAYMENT_TOKENS, COMMITTEE_SIZE, INITIAL_NETWORK_TRUST_SCORE, MAX_RECEIPT_HISTORY_BLOCKS, NEWRL_DB
from app.config.ntypes import BLOCK_STATUS_MINING_TIMEOUT, BLOCK_VOTE_MINER, NEWRL_TOKEN_CODE, NEWRL_TOKEN_DECIMAL, NEWRL_TOKEN_MULTIPLIER, NEWRL_TOKEN_NAME, NUSD_TOKEN_CODE, NUSD_TOKEN_MULTIPLIER, TRANSACTION_MINER_ADDITION, TRANSACTION_ONE_WAY_TRANSFER, TRANSACTION_SC_UPDATE, TRANSACTION_SMART_CONTRACT, TRANSACTION_TOKEN_CREATION, TRANSACTION_TRUST_SCORE_CHANGE, TRANSACTION_TWO_WAY_TRANSFER, TRANSACTION_WALLET_CREATION

logger = logging.getLogger(__name__)

value_txns = []


def update_db_states(cur, block):
    newblockindex = block['index'] if 'index' in block else block['block_index']
    transactions = block['text']['transactions']

    add_tx_to_block(cur, newblockindex, transactions)

    if 'creator_wallet' in block and block['creator_wallet'] is not None:
        add_block_reward(cur, block['creator_wallet'], newblockindex)

    global config_updated
    config_updated = False
    for transaction in transactions:
        try:
            if transaction['transaction']['type']== TRANSACTION_SMART_CONTRACT:
                handle_sc_transaction(cur,transaction,block['creator_wallet'],newblockindex)
            else:
                handle_txn(cur, transaction,newblockindex,newblockindex)
        except Exception as e:
            txn_code = transaction["transaction"]['trans_code']
            logger.error(f'Error in transaction: {str(txn_code)}')
            logger.error(str(e))
            logger.error(traceback.format_exc()) 
    if config_updated:
        Configuration.updateDataFromDB(cur)
    return True

def handle_txn(cur,transaction,newblockindex, creator_wallet):
    transaction_all = transaction
    transaction = transaction['transaction']
    transaction_data = transaction['specific_data']
    while isinstance(transaction_data, str):
        transaction_data = json.loads(transaction_data)
        transaction['specific_data']=transaction_data

    transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction[
        'trans_code']
    
    if newblockindex > 60000:  # prior to this block, the account balance could've been negative
        if not pay_fee_for_transaction(cur, transaction, creator_wallet):
            logger.error(f'Fee payment failed for transaction {transaction_code}')
            #TODO capture the reason and update as txn status 
            return

        tm = Transactionmanager()
        tm.set_transaction_data(transaction_all)
        tm.transactioncreator(transaction_all)
        if not tm.econvalidator(cur=cur):
            #TODO capture the reason and update as txn status
            return
    else:
        tm = Transactionmanager()
        tm.set_transaction_data(transaction_all)
        tm.transactioncreator(transaction_all)
        if not tm.econvalidator(cur=cur):
            #TODO capture the reason and update as txn status
            return
        
        if not pay_fee_for_transaction(cur, transaction, creator_wallet):
            logger.error(f'Fee payment failed for transaction {transaction_code}')
                #TODO capture the reason and update as txn status
            return
    process_txn(cur, transaction_all,newblockindex)  #TODO capture excpetion reason and update as txn status     

def process_txn(cur, transaction, newblockindex):
    signature = transaction['signatures']
    transaction = transaction['transaction']
    transaction_data = transaction['specific_data']
    while isinstance(transaction_data, str):
            transaction_data = json.loads(transaction_data)
            transaction['specific_data']=transaction_data

    transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction[
            'trans_code']

    try:
        update_state_from_transaction(
                cur,
                transaction['type'],
                transaction_data,
                transaction_code,
                transaction['timestamp'],
                signature,
                newblockindex,
                transaction
            )
    except Exception as e:
            logger.error(f'Error in transaction: {str(transaction)}')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            raise e
            #TODO capture the reason and update as txn status


def update_state_from_transaction(cur, transaction_type, transaction_data, transaction_code, transaction_timestamp,
                                  transaction_signer=None, block_index=None, full_transaction=None):
    if transaction_type == TRANSACTION_WALLET_CREATION:  # this is a wallet creation transaction
        add_wallet_pid(cur, transaction_data)

    if transaction_type == TRANSACTION_TOKEN_CREATION:  # this is a token creation or addition transaction
        
        edit_transaction =  transaction_data.get('token_update', False)

        if not edit_transaction:
            add_token(cur, transaction_data, transaction_code)
        else:
            update_token(cur, transaction_data,transaction_code)    

    if transaction_type == TRANSACTION_TWO_WAY_TRANSFER:  # this is a transfer tx
        sender1 = transaction_data['wallet1']

        #wallet other than wallet one is inferred as wallet2 , assuming only two sigs are present
        
        if transaction_data['wallet2'] is not None:
            sender2 = transaction_data['wallet2']
        else:
            if transaction_signer[0]["wallet_address"] == sender1:
                sender2 = transaction_signer[1]["wallet_address"]
            else:
                sender2 = transaction_signer[0]["wallet_address"]


        tokencode1 = transaction_data['asset1_code']
        amount1 = int(transaction_data['asset1_number'] or 0)
        transfer_tokens_and_update_balances(
            cur, sender1, sender2, tokencode1, amount1)

        tokencode2 = transaction_data['asset2_code']
        amount2 = int(transaction_data['asset2_number'] or 0)
        transfer_tokens_and_update_balances(
            cur, sender2, sender1, tokencode2, amount2)

    if transaction_type == TRANSACTION_ONE_WAY_TRANSFER:
        sender = transaction_data['wallet1']
        receiver = transaction_data['wallet2']
        token_code = transaction_data['asset1_code']
        amount = int(transaction_data['asset1_number'] or 0)

        transfer_tokens_and_update_balances(
            cur, sender, receiver, token_code, amount)

    if transaction_type == TRANSACTION_TRUST_SCORE_CHANGE:  # score update transaction
        personid1 = get_pid_from_wallet(cur, transaction_data['address1'])
        personid2 = get_pid_from_wallet(cur, transaction_data['address2'])
        new_score = transaction_data['new_score']
        tstamp = transaction_timestamp
        update_trust_score(cur, personid1, personid2, new_score, tstamp)


    if transaction_type == TRANSACTION_MINER_ADDITION:
        add_miner(
            cur,
            transaction_data['wallet_address'],
            transaction_data['network_address'],
            transaction_data['broadcast_timestamp'],
            block_index
        )
    if transaction_type == TRANSACTION_SC_UPDATE:
        cr = CentralRepository(cur, cur)
        global config_updated
        if(transaction_data['operation'] == "save"):
            cr.save_private_sc_state(
                transaction_data['table_name'], transaction_data["data"])
            if transaction_data['table_name']=='configuration':
                # Call to update the constants
                config_updated=True
        if(transaction_data['operation'] == "update"):
            cr.update_private_sc_state(transaction_data['table_name'], transaction_data["data"],
                                       transaction_data["unique_column"], transaction_data["unique_value"], transaction_data["address"])
            if transaction_data['table_name']=='configuration':
                # Call to update the constants

                config_updated=True
        if(transaction_data['operation'] == "delete"):
            cr.delete_private_sc_state(transaction_data['table_name'], transaction_data["unique_column"],
                                       transaction_data["unique_value"], transaction_data["address"])



def add_block_reward(cur, creator, blockindex):
    """Reward the minder by chaning their NWRL balance"""
    if creator is None:
        return False
    reward = 0
    RATIO = 0.99
    STARTING_REWARD = 100
    block_step = math.ceil(float(blockindex) / 1000000)
    reward = math.floor(STARTING_REWARD * pow(RATIO, (block_step - 1)) * pow(10, NEWRL_TOKEN_DECIMAL))
    reward_tx_data = {
        "tokenname": NEWRL_TOKEN_NAME,
        "tokencode": NEWRL_TOKEN_CODE,
        "tokentype": '1',
        "tokenattributes": {},
        "first_owner": creator,
        "custodian": '',
        "legaldochash": '',
        "amount_created": reward,
        "disallowed": {},
        "sc_flag": False
    }
    add_token(cur, reward_tx_data)
    return True


def update_trust_scores(cur, block):
    if 'previous_block_receipts' not in block['text']:
        return
    receipts = block['text']['previous_block_receipts']

    for receipt in receipts:
        if receipt['data']['block_index'] > block['index'] - MAX_RECEIPT_HISTORY_BLOCKS:
            update_network_trust_score_from_receipt(cur, receipt=receipt)

def update_miners(cur, block):
    if (
        block['expected_miner'] != block['creator_wallet']
        and block['status'] == BLOCK_STATUS_MINING_TIMEOUT
    ):
        logger.info('Removing miner %s due to timeout', block['expected_miner'])
        cur.execute('DELETE FROM miners WHERE wallet_address = ?', (block['expected_miner'], ))

def simplify_transactions_sc(cur, transaction):
  global value_txns
  simplified_transactions = []
  simplified_transactions.append('SC_START')
  simplified_transactions.append(transaction)

  try:
    non_sc_txns = get_non_sc_txns(cur, transaction)
    simplified_transactions.extend(value_txns)
    simplified_transactions.extend(non_sc_txns)
  except Exception as e:
    value_txns = []
    logger.error(f"Exception during sc txn execution for txn : {transaction}")
    logger.error(traceback.format_exc())  
    raise e
  
  simplified_transactions.append('SC_END')
  value_txns = []
  return simplified_transactions  


def get_non_sc_txns(cur, transaction):
    child_transactions = execute_sc(cur, transaction)
    simplified_child_transactions = []
    for child_transaction in child_transactions:
        logger.info("Processing child transaction" + str(child_transaction))
        if not validate_sc_child_transaction(child_transaction, transaction['transaction']["specific_data"]["address"]):
            raise Exception("Sc child txn validation chain failed")
        if(child_transaction.transaction['type'] == TRANSACTION_SMART_CONTRACT):
            non_sc_child_txns = get_non_sc_txns(
                cur, child_transaction.get_transaction_complete())
            simplified_child_transactions.extend(non_sc_child_txns)
        else:
            simplified_child_transactions.append(
                child_transaction.get_transaction_complete())
    return simplified_child_transactions


def execute_sc(cur, transaction_main):
    transaction = transaction_main["transaction"]
    transaction_data = transaction['specific_data']
    while isinstance(transaction_data, str):
        transaction_data = json.loads(transaction_data)
        transaction['specific_data'] = transaction_data
    transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction[
        'trans_code']
    transaction_signer = transaction_main['signatures']

    global value_txns

    funct = transaction_data['function']
    if funct == "setup":  # sc is being set up
        contract = dict(transaction_data['params'])
        transaction_data['params']['parent'] = transaction_code
    else:
        contract = get_contract_from_address(cur, transaction_data['address'])
    module = importlib.import_module(
        ".core.contracts." + contract['name'], package="app")
    sc_class = getattr(module, contract['name'])
    sc_instance = sc_class(transaction_data['address'])
    funct = getattr(sc_instance, funct)
    params_for_funct = transaction_data['params']
    params_for_funct['function_caller'] = transaction_signer
    try:
        fetchRepository = FetchRepository(cur)
        sc_value_txns = get_value_txns(transaction_signer, transaction_data)
        value_txns.extend(sc_value_txns)
        child_transactions = funct(params_for_funct, fetchRepository)
        #if value is present then make a child txn 5 based on it (it will be validated as part of child sc validation)
        return child_transactions
    except Exception as e:
        print(
            f"Exception during smart contract function execution for transaction {transaction_code} + {e}")
        logger.error(e)
        raise Exception(e)
    pass


def validate_sc_child_transaction(transaction: Transactionmanager, contract_address):
    return validate(transaction, contract_address)


def get_value_txns(transaction_signer, transaction_data):

    if 'value' not in transaction_data['params']:
        return []

    transaction_creator = TransactionCreator()
    value_details = transaction_data['params']['value']
    sender = transaction_signer[0]['wallet_address']
    receiver = transaction_data['address']
    value_txns_local = []

    for value in value_details:
        transfer_proposal_data = {
            "transfer_type": 1,
            "asset1_code": value['token_code'],
            "asset2_code": "",
            "wallet1": sender,
            "wallet2": receiver,
            "asset1_number": value['amount'],
            "asset2_number": 0,
            "additional_data": {
            }
        }
        transfer_proposal = transaction_creator.transaction_type_5(
            transfer_proposal_data)
        if not transfer_proposal.econvalidator()['validity']:
            logger.error(
                "SC-value txn economic validation failed for transaction")
            raise Exception("SC-value txn validation failed for transaction")
        value_txns_local.append(transfer_proposal.get_transaction_complete())
    return value_txns_local

def get_fees_for_transaction(transaction):
    if 'fee' in transaction:
        return transaction['fee']
    else:
        return 0


def pay_fee_for_transaction(cur, transaction, creator):
    if 'transaction' in transaction:
        transaction = transaction['transaction']

    if transaction['type'] in [TRANSACTION_MINER_ADDITION, TRANSACTION_SC_UPDATE]:
        return True

    fee = get_fees_for_transaction(transaction)

    if fee < 0:
        return False

    currency = transaction['currency']

    if currency == NEWRL_TOKEN_CODE:
        if fee < NEWRL_TOKEN_MULTIPLIER:
            return False
    elif currency == NUSD_TOKEN_CODE:
        if fee < NUSD_TOKEN_MULTIPLIER:
            return False
    else:
        return False

    if 'fee_payer' in transaction:
        payers = [transaction['fee_payer']]
    else:
        payers = get_valid_addresses(transaction, cur=cur)

    for payee in payers:
        balance = get_wallet_token_balance(cur, payee, currency)
        fee_to_charge = math.ceil(fee / len(payers))
        if balance < fee_to_charge:  # TODO - This should also account for payout/values in the transaction
            return False
        transfer_tokens_and_update_balances(
            cur,
            payee,
            TREASURY_WALLET_ADDRESS,
            transaction['currency'],
            int(fee_to_charge * 0.8)
        )
        transfer_tokens_and_update_balances(
            cur,
            payee,
            creator,
            transaction['currency'],
            fee_to_charge - int(fee_to_charge * 0.8)
        )
    return True

def handle_sc_transaction(cur, transaction, creator_wallet, newblockindex):
    
    transaction_all = transaction
    transaction = transaction['transaction']
    transaction_data = transaction['specific_data']
    while isinstance(transaction_data, str):
            transaction_data = json.loads(transaction_data)
            transaction['specific_data']=transaction_data

    transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction[
            'trans_code']
    
    sc_txns_simplified = simplify_transactions_sc(cur = cur, transaction= transaction_all)
    for transaction in sc_txns_simplified:

        if transaction == 'SC_START':
            cur.execute(f'SAVEPOINT sc_start')
        elif transaction == 'SC_END':
            cur.execute(f'RELEASE SAVEPOINT sc_start')
        else:
        #use root txn and pay for fee. If fee cant be paid, break
            if transaction['transaction']['type'] == TRANSACTION_SMART_CONTRACT:
                if not pay_fee_for_transaction(cur, transaction, creator_wallet):
                    cur.execute(f'ROLLBACK to SAVEPOINT sc_start')
                    break    
                continue

            transaction_all = transaction
            transaction = transaction['transaction']
            transaction_data = transaction['specific_data']
            while isinstance(transaction_data, str):
                transaction_data = json.loads(transaction_data)
                transaction['specific_data']=transaction_data

            transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction['trans_code']    
    
            tm = Transactionmanager()
            tm.set_transaction_data(transaction_all)
            tm.transactioncreator(transaction_all)
            if not tm.econvalidator(cur=cur):
                logger.error("Econ validation failed for sc txn")
                cur.execute(f'ROLLBACK to SAVEPOINT sc_start')
                break
            process_txn(cur,transaction_all,newblockindex)   
 

 
    
def state_cleanup(cur, block):
    return False  # Do not clean blocks
    # Delete old blocks as well. Not useful to keep them on light nodes.
    if not Configuration.conf['FULL_NODE']:
        cur.execute('DELETE FROM blocks where block_index < ?', (block['index'] - MAX_RECEIPT_HISTORY_BLOCKS * 2, ))
