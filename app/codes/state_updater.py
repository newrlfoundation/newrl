import math
import json
import importlib
from lib2to3.pgen2 import token
from app.codes.clock.global_time import get_corrected_time_ms

from app.nvalues import NETWORK_TRUST_MANAGER


from ..constants import NEWRL_DB
from .db_updater import *
from ..ntypes import NEWRL_TOKEN_CODE, NEWRL_TOKEN_NAME, TRANSACTION_MINER_ADDITION, TRANSACTION_ONE_WAY_TRANSFER, TRANSACTION_SMART_CONTRACT, TRANSACTION_TOKEN_CREATION, TRANSACTION_TRUST_SCORE_CHANGE, TRANSACTION_TWO_WAY_TRANSFER, TRANSACTION_WALLET_CREATION


def update_db_states(cur, block):
    newblockindex = block['index'] if 'index' in block else block['block_index']
    transactions = block['text']['transactions']
    # last_block_cursor = cur.execute(
    #     f'''SELECT block_index FROM blocks ORDER BY block_index DESC LIMIT 1''')
    # last_block = last_block_cursor.fetchone()
    # if newblockindex != last_block[0]:
    #     print("The latest block index does not match given previous index")
    #     return False
#    latest_index = cur.execute('SELECT MAX(block_index) FROM blocks')
    add_tx_to_block(cur, newblockindex, transactions)

    if 'creator_wallet' in block and block['creator_wallet'] is not None:
        add_block_reward(cur, block['creator_wallet'], newblockindex)

    for transaction in transactions:
        signature=transaction['signatures']
        transaction = transaction['transaction']
        transaction_data = transaction['specific_data']

        while isinstance(transaction_data, str):
            transaction_data = json.loads(transaction_data)

        transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction['trans_code']

        update_state_from_transaction(
            cur,
            transaction['type'],
            transaction_data,
            transaction_code,
            transaction['timestamp'],
            signature
        )
    return True


def update_state_from_transaction(cur, transaction_type, transaction_data, transaction_code, transaction_timestamp,transaction_signer=None):
    if transaction_type == TRANSACTION_WALLET_CREATION:  # this is a wallet creation transaction
        add_wallet_pid(cur, transaction_data)

    if transaction_type == TRANSACTION_TOKEN_CREATION:  # this is a token creation or addition transaction
        add_token(cur, transaction_data, transaction_code)

    if transaction_type == TRANSACTION_TWO_WAY_TRANSFER or transaction_type == TRANSACTION_ONE_WAY_TRANSFER:  # this is a transfer tx
        sender1 = transaction_data['wallet1']
        sender2 = transaction_data['wallet2']

        tokencode1 = transaction_data['asset1_code']
        amount1 = int(transaction_data['asset1_number'] or 0)
        transfer_tokens_and_update_balances(
            cur, sender1, sender2, tokencode1, amount1)

        tokencode2 = transaction_data['asset2_code']
        amount2 = int(transaction_data['asset2_number'] or 0)
        transfer_tokens_and_update_balances(
            cur, sender2, sender1, tokencode2, amount2)

    if transaction_type == TRANSACTION_TRUST_SCORE_CHANGE:  # score update transaction
        personid1 = get_pid_from_wallet(cur, transaction_data['address1'])
        personid2 = get_pid_from_wallet(cur, transaction_data['address2'])
        new_score = transaction_data['new_score']
        tstamp = transaction_timestamp
        update_trust_score(cur, personid1, personid2, new_score, tstamp)

    if transaction_type == TRANSACTION_SMART_CONTRACT:  # smart contract transaction
        funct = transaction_data['function']
        if funct == "setup":  # sc is being set up
            contract = dict(transaction_data['params'])
            transaction_data['params']['parent'] = transaction_code
        else:
            contract = get_contract_from_address(
                cur, transaction_data['address'])
        module = importlib.import_module(
            ".codes.contracts."+contract['name'], package="app")
        sc_class = getattr(module, contract['name'])
        sc_instance = sc_class(transaction_data['address'])
    #    sc_instance = nusd1(transaction['specific_data']['address'])
        funct = getattr(sc_instance, funct)
        params_for_funct=transaction_data['params']
        # adding singers address to the dict
        params_for_funct['function_caller']=transaction_signer
        try:
            funct(cur, params_for_funct)
        except Exception as e:
            print('Exception durint smart contract function run', e)
    if transaction_type == TRANSACTION_MINER_ADDITION:
        add_miner(
            cur,
            transaction_data['wallet_address'],
            transaction_data['network_address'],
            transaction_data['broadcast_timestamp'],
        )



def add_block_reward(cur, creator, blockindex):
    """Reward the minder by chaning their NWRL balance"""
    reward = 0
    RATIO = 2/3
    STARTING_REWARD = 1000
    block_step = math.ceil(float(blockindex)/1000000)
    reward = STARTING_REWARD * pow(RATIO, (block_step - 1))
    reward_tx_data = {
        "tokenname": NEWRL_TOKEN_NAME,
        "tokencode" : NEWRL_TOKEN_CODE,
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
    receipts = block['text']['previous_block_receipts']

    for receipt in receipts:
        wallet_cursor = cur.execute(
        'SELECT wallet_address FROM wallets where wallet_public=?', 
        (receipt['public_key'],)).fetchone()
    
        if wallet_cursor is not None:
            wallet_address = wallet_cursor[0]
            vote = receipt['data']['vote']

            trust_score_cursor = cur.execute('''
                SELECT score FROM trust_scores where src_person_id=? and dest_person_id=?
                ''', (NETWORK_TRUST_MANAGER, wallet_address)).fetchone()
            
            if trust_score_cursor is None:
                existing_score = 1
            else:
                existing_score = trust_score_cursor[0]

            # TODO - This logic might need to change condisering all the persons in chain
            if vote == 1:
                new_score = (existing_score + 1) / 2
            else:
                new_score = (existing_score - 1) / 2

            update_trust_score(cur, NETWORK_TRUST_MANAGER, wallet_address, new_score, get_corrected_time_ms())
