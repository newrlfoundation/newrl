import json
import logging
import sqlite3
from types import new_class
from typing import List

from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.params import File
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from starlette.requests import Request

from app.limiter import limiter
from app.codes.helpers.FetchRespository import FetchRepository
from app.codes.p2p.sync_chain import find_forking_block, get_block_hashes, get_blocks
from app.codes.scoremanager import get_incoming_trust_scores, get_outgoing_trust_scores, get_trust_score, get_trust_score_for_wallets

from app.codes.transactionmanager import Transactionmanager
from app.constants import NEWRL_DB
from app.nvalues import NETWORK_TRUST_MANAGER_PID

from .request_models import AddWalletRequest, BalanceRequest, BalanceType, CallSC, CreateTokenRequest, CreateWalletRequest, GetTokenRequest, RunSmartContractRequest, TransferRequest, CreateSCRequest, TrustScoreUpdateRequest
from app.codes.chainscanner import Chainscanner, download_chain, download_state, get_block, get_contract, get_token, get_transaction, get_wallet
from app.codes.kycwallet import add_wallet, generate_wallet_address, get_address_from_public_key, get_digest, generate_wallet
from app.codes.tokenmanager import create_token_transaction
from app.codes.transfermanager import Transfermanager
from app.codes.utils import get_last_block_hash, save_file_and_get_path
from app.codes import validator
from app.codes import signmanager
from app.codes import updater
from app.codes.aggregator import process_transaction_batch
from app.codes.contracts.contract_master import create_contract_address
from ..Configuration import Configuration

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

query_tag = 'Query APIs'
submit_tag = 'Submit APIs'
legacy = 'Legacy'
system = "System"


@router.get("/get-block", tags=[query_tag])
def get_block_api(block_index: str):
    """Get a block from the chain"""
    block = get_block(block_index)
    if block is None:
        raise HTTPException(status_code=400, detail="Block not found")
    return block

@router.get("/get-transaction", tags=[query_tag])
def get_transaction_api(transaction_code: str):
    """Get a transaction from the chain"""
    transaction = get_transaction(transaction_code)
    if transaction is None:
        raise HTTPException(status_code=400, detail="Transaction not found")
    return transaction

@router.get("/get-wallet", tags=[query_tag])
def get_wallet_api(wallet_address: str):
    """Get a wallet details from the chain"""
    wallet = get_wallet(wallet_address)
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    return wallet

@router.get("/get-token", tags=[query_tag])
def get_token_api(token_code: str):
    """Get a token details from the chain"""
    wallet = get_token(token_code)
    if wallet is None:
        raise HTTPException(status_code=400, detail="Token not found")
    return wallet

@router.get("/get-balances", tags=[query_tag])
def get_balances_api(balance_type: BalanceType, token_code: str = "", wallet_address: str = ""):
    chain_scanner = Chainscanner()
    if balance_type == BalanceType.TOKEN_IN_WALLET:
        balance = chain_scanner.getbaladdtoken(
            wallet_address, str(token_code))
    elif balance_type == BalanceType.ALL_TOKENS_IN_WALLET:
        balance = chain_scanner.getbalancesbyaddress(wallet_address)
    elif balance_type == BalanceType.ALL_WALLETS_FOR_TOKEN:
        balance = chain_scanner.getbalancesbytoken(str(token_code))
    return {'balance': balance}


@router.get("/get-contract", tags=[query_tag])
def get_contract_api(contract_address: str):
    """Get a contract details from the chain"""
    contract = get_contract(contract_address)
    if contract is None:
        raise HTTPException(status_code=400, detail="Contract not found")
    return contract


@router.get("/get-trustscore-pid", tags=[query_tag])
def get_trust_score_api(
        destination_person_id: str,
        source_person_id: str=Configuration.config("NETWORK_TRUST_MANAGER_PID")):
    """Get a trust score. Default source_person_id is network trust manager"""
    trust_score = get_trust_score(src_person_id=source_person_id, dest_person_id=destination_person_id)
    if trust_score is None:
        raise HTTPException(status_code=400, detail="Trust score not available")
    return {'trust_score': trust_score}


@router.get("/get-trustscore-wallets", tags=[query_tag])
def get_trust_score_api(
        src_wallet_address: str,
        dst_wallet_address: str):
    """Get a trust score. Default source_person_id is network trust manager"""
    trust_score = get_trust_score_for_wallets(src_wallet_address, dst_wallet_address)
    if trust_score is None:
        raise HTTPException(status_code=400, detail="Trust score not available")
    return {'status': 'SUCCESS', 'trust_score': trust_score}


@router.get("/get-incoming-trustscores", tags=[query_tag])
def get_trust_score_api(
        dst_wallet_address: str):
    """Get a trust score. Default source_person_id is network trust manager"""
    trust_score = get_incoming_trust_scores(dst_wallet_address)
    if trust_score is None:
        raise HTTPException(status_code=400, detail="Trust score not available")
    return {'status': 'SUCCESS', 'trust_score': trust_score}


@router.get("/get-outgoing-trustscores", tags=[query_tag])
def get_trust_score_api(
        src_wallet_address: str):
    """Get a trust score. Default source_person_id is network trust manager"""
    trust_score = get_outgoing_trust_scores(src_wallet_address)
    if trust_score is None:
        raise HTTPException(status_code=400, detail="Trust score not available")
    return {'status': 'SUCCESS', 'trust_score': trust_score}


# @router.post("/get-balance", tags=[legacy])
# def get_balance(req: BalanceRequest):
#     chain_scanner = Chainscanner()
#     if req.balance_type == BalanceType.TOKEN_IN_WALLET:
#         balance = chain_scanner.getbaladdtoken(
#             req.wallet_address, str(req.token_code))
#     elif req.balance_type == BalanceType.ALL_TOKENS_IN_WALLET:
#         balance = chain_scanner.getbalancesbyaddress(req.wallet_address)
#     elif req.balance_type == BalanceType.ALL_WALLETS_FOR_TOKEN:
#         balance = chain_scanner.getbalancesbytoken(str(req.token_code))
#     return {'balance': balance}

@router.get("/get-address-from-publickey", tags=[query_tag], include_in_schema=False)
def get_address_from_public_key_api(public_key: str):
    try:
        address = get_address_from_public_key(public_key)
        return {'address': address}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate-wallet-address", tags=[query_tag], include_in_schema=False)
def generate_wallet_address_api():
    return generate_wallet_address()

# v2 APIs - JSON only

@router.get("/generate-contract-address", tags=[query_tag], include_in_schema=False)
def generate_contract_address_api():
    return create_contract_address()

@router.post("/add-wallet", tags=[query_tag], include_in_schema=False)
def add_wallet_api(req: AddWalletRequest):
    """Get a transaction file for adding an existing wallet to chain"""
    try:
        req_dict = req.dict()
        add_wallet_transaction = add_wallet(req.custodian_address, req_dict['kyc_docs'], req.ownertype, 
            req.jurisdiction, req.public_key, req.specific_data)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    with open(add_wallet_transaction) as f:
        return json.load(f)
    # return FileResponse(add_wallet_transaction, filename="add_wallet_transaction.json")

@router.post("/add-token", tags=[query_tag], include_in_schema=False)
def add_token(
    request: CreateTokenRequest
):
    token_data = {
        "tokenname": request.token_name,
        "tokencode" : request.token_code,
        "tokentype": request.token_type,
        "tokenattributes": request.token_attributes,
        "first_owner": request.first_owner,
        "custodian": request.custodian,
        "legaldochash": request.legal_doc,
        "amount_created": request.amount_created,
        "tokendecimal": request.tokendecimal,
        "disallowed": request.disallowed_regions,
        "sc_flag": request.is_smart_contract_token
    }
    try:
        token_create_transaction_filename = create_token_transaction(token_data)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    with open(token_create_transaction_filename) as f:
        return json.load(f)

@router.post("/add-transfer", tags=[query_tag], include_in_schema=False)
def add_transfer(transfer_request: TransferRequest):
    """Used to create a transfer file which can be signed and executed by /sign and /transfer respectively"""
    transfer_type = transfer_request.transfer_type
    trandata = {
        "transfer_type": transfer_type,
        "asset1_code": str(transfer_request.asset1_code),
        "asset2_code": str(transfer_request.asset2_code),
        "wallet1": transfer_request.wallet1_address,
        "wallet2": transfer_request.wallet2_address,
        "asset1_number": int(transfer_request.asset1_qty),
        "asset2_number": int(transfer_request.asset2_qty),
        "additional_data": transfer_request.additional_data
    }
    type = transfer_request.transfer_type
    fulltrandata = {
        "transaction": {
            "timestamp": "",
            "trans_code": "000000",
            "type": type,
            "currency": "NWRL",
            "fee": 0.0,
            "descr": transfer_request.description,
            "valid": 1,
            "block_index": 0,
            "specific_data": trandata
        },
        "signatures": []
    }
    # with open("transfernew.json", 'w') as file:
    #     json.dump(fulltrandata, file)

    newtransfer = Transfermanager(transfer_data=fulltrandata)
    tdatanew = newtransfer.loadandcreate()
    return tdatanew
#    with open("./transfernew.json","r") as tfile:
#        transferfile_path = save_file_and_get_path(tfile)
#    transferfile = FileResponse(
#        "transfernew.json", filename="transferfile.json")
#    with open("transfernew.json") as f:
#        return json.load(f)

@router.post("/add-sc", tags=[query_tag], include_in_schema=False)
def add_sc(sc_request: CreateSCRequest):
    """Used to create a sc object which can be used to set up and deploy a smart contract"""
    scdata = {
        "creator":sc_request.creator,
        "ts_init":None,
        "name":sc_request.sc_name,
        "version":sc_request.version,
        "actmode":sc_request.actmode,
        "status":0,
        "next_act_ts":None,
        "signatories":sc_request.signatories,
        "parent":None,
        "oracleids":None,
        "selfdestruct":1,
        "contractspecs":sc_request.contractspecs,
        "legalparams":sc_request.legalparams
        }

    txspecdata = {
        "address": sc_request.sc_address,
        "function" : "setup",
        "signers" : [sc_request.creator],
        "params" : scdata
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
#    with open("transfernew.json", 'w') as file:
#        json.dump(fulltrandata, file)
    newsc = Transactionmanager()
    tdatanew = newsc.transactioncreator(fulltrandata)
    return tdatanew

@router.post("/call-sc", tags=[query_tag], include_in_schema=False)
def call_sc(sc_request: CallSC):
    """Used to create a sc object which can be used to set up and deploy a smart contract"""

    txspecdata = {
        "address": sc_request.sc_address,
        "function" : sc_request.function_called,
        "signers" : sc_request.signers,
        "params" : sc_request.params
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
#    with open("transfernew.json", 'w') as file:
#        json.dump(fulltrandata, file)
    newtx = Transactionmanager()
    tdatanew = newtx.transactioncreator(fulltrandata)
    return tdatanew

@router.post("/update-trustscore", tags=[query_tag], include_in_schema=False)
def update_trustscore_wallet(ts_request: TrustScoreUpdateRequest):
    """Used to update trust score of person1 for person 2 """

    txspecdata = {
        "address1": ts_request.source_address,
        "address2": ts_request.destination_address,
        "new_score" : ts_request.tscore,
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
#    with open("transfernew.json", 'w') as file:
#        json.dump(fulltrandata, file)
    newtx = Transactionmanager()
    tdatanew = newtx.transactioncreator(fulltrandata)
    return tdatanew

@router.post("/sign-transaction", tags=[query_tag], include_in_schema=False)
def sign_transaction(wallet_data: dict, transaction_data: dict):
    """Custodian wallet file can be used to sign a transaction"""
    # transactionfile_path = save_file_and_get_path(transactionfile)
    # wallet_file = save_file_and_get_path(wallet_file)
    singed_transaction_file = signmanager.sign_transaction(wallet_data, transaction_data)
    return singed_transaction_file

@router.post("/submit-transaction", tags=[submit_tag])
@limiter.limit("1/second")
async def submit_transaction(request: Request):
    """Submit a signed transaction and adds it to the chain"""
    try:
        request_body = await request.json()
        print('Received transaction: ', request_body)
        response = validator.validate(request_body, propagate=True, validate_economics=True)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "SUCCESS", "response": response}


@router.post("/submit-transaction-batch", tags=[submit_tag])
@limiter.limit("10/minute")
async def submit_transactions(request: Request):
    """
        Submit a list of signed transactions to 
    """
    try:
        request_body = await request.json()
        new_transactions = process_transaction_batch(request_body)
        response = {
            'accepted_transactions': len(new_transactions)
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "SUCCESS", "response": response}

    
@router.post("/validate-transaction", tags=[query_tag], include_in_schema=False)
def validate_transaction(transaction_data: dict, include_in_schema=False):
    """Validate a signed transaction and adds it to the chain"""
    try:
        print('Received transaction: ', transaction_data)
        response = validator.validate(transaction_data, propagate=True, validate_economics=True)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "SUCCESS", "response": response}



@router.post("/run-updater", tags=[system], include_in_schema=False)
def run_updater(add_to_chain_before_consensus: bool = False):
    try:
        # log = updater.run_updater()
        updater.mine(add_to_chain_before_consensus)
        return {'status': 'SUCCESS'}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    # HTMLResponse(content=log, status_code=200)
    # return log

@router.get("/sc-state",tags=[query_tag])
def get_sc_state(table_name, contract_address, unique_column, unique_value):
    try:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        repo = FetchRepository(cur)

        data = repo.select_Query().add_table_name(table_name).where_clause(unique_column, unique_value, 1).and_clause(
            "address", contract_address,1).execute_query_single_result({unique_column: unique_value, "address": contract_address})

        con.close()
        resp = {"status": "SUCCESS", 'data': data}
        return resp
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sc-states", tags=[query_tag])
def get_sc_states(table_name, contract_address):
    try:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        repo = FetchRepository(cur)

        data = repo.select_Query().add_table_name(table_name).where_clause("address", contract_address, 1).execute_query_multiple_result({"address": contract_address})

        con.close()
        resp = {"status": "SUCCESS", 'data': data}
        return resp
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-last-block-hash", tags=[query_tag])
def get_last_block_hash_api():
    """Get a block from the chain"""
    block = get_last_block_hash()
    if block is None:
        raise HTTPException(status_code=400, detail="Block not found")
    return block


@router.get("/get-block-tree", tags=[query_tag], include_in_schema=False)
def get_block_tree_api(start_index: int, end_index: int):
    """Get block tree for given start and end"""
    blocks = get_block_hashes(start_index, end_index)
    blocks = list(blocks)
    return blocks


@router.get("/find-forking-block", tags=[query_tag], include_in_schema=False)
def get_fork_block(url: str):
    return find_forking_block(url)
