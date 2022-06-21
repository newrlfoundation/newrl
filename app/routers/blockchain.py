import json
import logging
from types import new_class

from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.params import File
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

from app.codes.transactionmanager import Transactionmanager

from .request_models import AddWalletRequest, BalanceRequest, BalanceType, CallSC, CreateTokenRequest, CreateWalletRequest, GetTokenRequest, RunSmartContractRequest, TransferRequest, CreateSCRequest, TscoreRequest
from app.codes.chainscanner import Chainscanner, download_chain, download_state, get_block, get_contract, get_token, get_transaction, get_wallet
from app.codes.kycwallet import add_wallet, generate_wallet_address, get_address_from_public_key, get_digest, generate_wallet
from app.codes.tokenmanager import create_token_transaction
from app.codes.transfermanager import Transfermanager
from app.codes.utils import save_file_and_get_path
from app.codes import validator
from app.codes import signmanager
from app.codes import updater
from app.codes.contracts.contract_master import create_contract_address

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

v2_tag = 'Blockchain'
legacy = 'Legacy'
system = "System"


@router.get("/get-block", tags=[v2_tag])
def get_block_api(block_index: str):
    """Get a block from the chain"""
    block = get_block(block_index)
    if block is None:
        raise HTTPException(status_code=400, detail="Block not found")
    return block

@router.get("/get-transaction", tags=[v2_tag])
def get_transaction_api(transaction_code: str):
    """Get a transaction from the chain"""
    transaction = get_transaction(transaction_code)
    if transaction is None:
        raise HTTPException(status_code=400, detail="Transaction not found")
    return transaction

@router.get("/get-wallet", tags=[v2_tag])
def get_wallet_api(wallet_address: str):
    """Get a wallet details from the chain"""
    wallet = get_wallet(wallet_address)
    if wallet is None:
        raise HTTPException(status_code=400, detail="Wallet not found")
    return wallet

@router.get("/get-token", tags=[v2_tag])
def get_token_api(token_code: str):
    """Get a token details from the chain"""
    wallet = get_token(token_code)
    if wallet is None:
        raise HTTPException(status_code=400, detail="Token not found")
    return wallet

@router.get("/get-balances", tags=[v2_tag])
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


@router.get("/get-contract", tags=[v2_tag])
def get_contract_api(contract_address: str):
    """Get a contract details from the chain"""
    contract = get_contract(contract_address)
    if contract is None:
        raise HTTPException(status_code=400, detail="Contract not found")
    return contract

@router.get("/download-chain", tags=[v2_tag])
def download_chain_api():
    return download_chain()


@router.get("/download-state", tags=[v2_tag])
def download_state_api():
    return download_state()


@router.post("/get-balance", tags=[legacy])
def get_balance(req: BalanceRequest):
    chain_scanner = Chainscanner()
    if req.balance_type == BalanceType.TOKEN_IN_WALLET:
        balance = chain_scanner.getbaladdtoken(
            req.wallet_address, str(req.token_code))
    elif req.balance_type == BalanceType.ALL_TOKENS_IN_WALLET:
        balance = chain_scanner.getbalancesbyaddress(req.wallet_address)
    elif req.balance_type == BalanceType.ALL_WALLETS_FOR_TOKEN:
        balance = chain_scanner.getbalancesbytoken(str(req.token_code))
    return {'balance': balance}

@router.get("/get-address-from-publickey", tags=[v2_tag])
def get_address_from_public_key_api(public_key: str):
    try:
        address = get_address_from_public_key(public_key)
        return {'address': address}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate-wallet-address", tags=[v2_tag])
def generate_wallet_address_api():
    return generate_wallet_address()

# v2 APIs - JSON only

@router.get("/generate-contract-address", tags=[v2_tag])
def generate_contract_address_api():
    return create_contract_address()

@router.post("/add-wallet", tags=[v2_tag])
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

@router.post("/add-token", tags=[v2_tag])
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

@router.post("/add-transfer", tags=[v2_tag])
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

@router.post("/add-sc", tags=[v2_tag])
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

@router.post("/call-sc", tags=[v2_tag])
def call_sc(sc_request: CallSC):
    """Used to create a sc object which can be used to set up and deploy a smart contract"""

    txspecdata = {
        "address": sc_request.sc_address,
        "function" : sc_request.function_called,
        "signers" : sc_request.signers,
        "params" : sc_request.params,
        "value": sc_request.value
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

@router.post("/update-trustscore", tags=[v2_tag])
def update_ts(ts_request: TscoreRequest):
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

@router.post("/sign-transaction", tags=[v2_tag])
def sign_transaction(wallet_data: dict, transaction_data: dict):
    """Custodian wallet file can be used to sign a transaction"""
    # transactionfile_path = save_file_and_get_path(transactionfile)
    # wallet_file = save_file_and_get_path(wallet_file)
    singed_transaction_file = signmanager.sign_transaction(wallet_data, transaction_data)
    return singed_transaction_file

@router.post("/submit-transaction", tags=[v2_tag])
def submit_transaction(transaction_data: dict):
    """Submit a signed transaction and adds it to the chain"""
    try:
        print('Received transaction: ', transaction_data)
        response = validator.validate(transaction_data, propagate=True, validate_economics=True)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "SUCCESS", "response": response}
    
@router.post("/validate-transaction", tags=[v2_tag])
def validate_transaction(transaction_data: dict):
    """Validate a signed transaction and adds it to the chain"""
    try:
        print('Received transaction: ', transaction_data)
        response = validator.validate(transaction_data, propagate=True, validate_economics=True)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "SUCCESS", "response": response}



@router.post("/run-updater", tags=[system])
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