"""Transaction management functions"""
import importlib
from logging import Logger
import logging
import math
from re import A
import time
import ecdsa
import os
import hashlib
import json
import datetime
import base64
import sqlite3

from app.core.db.db_updater import get_contract_from_address, get_wallet_token_balance
from app.core.helpers.CustomExceptions import ContractValidationError
from app.core.helpers.FetchRespository import FetchRepository
from app.config.Configuration import Configuration
from app.config.nvalues import CUSTODIAN_DAO_ADDRESS


from app.config.ntypes import NEWRL_TOKEN_CODE, NEWRL_TOKEN_MULTIPLIER, NUSD_TOKEN_CODE, TRANSACTION_MINER_ADDITION, TRANSACTION_ONE_WAY_TRANSFER, TRANSACTION_SC_UPDATE, TRANSACTION_SMART_CONTRACT, TRANSACTION_TRUST_SCORE_CHANGE, TRANSACTION_TWO_WAY_TRANSFER, TRANSACTION_WALLET_CREATION, TRANSACTION_TOKEN_CREATION,TOKEN_NFT

from app.config.constants import CUSTODIAN_OWNER_TYPE, MEMPOOL_PATH, NEWRL_DB
from app.core.helpers.utils import get_person_id_for_wallet_address, get_time_ms

logger = logging.getLogger(__name__)


class Transactionmanager:
    def __init__(self):
        self.transaction = {
            'timestamp': get_time_ms(),
            'trans_code': "0000",
            'type': 0,
            'currency': "NWRL",
            'fee': 0.0,
            'descr': None,
            'valid': 1,
            'specific_data': {}
        }

        self.signatures = []
        self.mempool = MEMPOOL_PATH
        self.validity = 0

    def get_valid_addresses(self):
        """Get valid signature addresses for a transaction"""
        return get_valid_addresses(self.transaction)

    def transactioncreator(self, tran_data_all):
        """
            Standard data concerns static fields, specific data
            covers fields that are type specific
        """

        tran_data = tran_data_all['transaction']
        if not tran_data['timestamp']:
            self.transaction['timestamp'] = get_time_ms()
        else:
            self.transaction['timestamp'] = tran_data['timestamp']

        self.transaction['type'] = tran_data['type']
        self.transaction['currency'] = tran_data['currency']
        self.transaction['fee'] = tran_data['fee']
        self.transaction['descr'] = tran_data['descr']
        self.transaction['valid'] = 1  # default at creation is unverified
        self.transaction['specific_data'] = tran_data['specific_data']
        self.transaction['is_child_txn'] = True if 'is_child_txn' in tran_data else False
        trstr = json.dumps(self.transaction).encode()
        hs = hashlib.blake2b(digest_size=20)
        hs.update(trstr)
        self.transaction['trans_code'] = hs.hexdigest()
        self.signatures = tran_data_all['signatures']
        transaction_all = {'transaction': self.transaction,
                           'signatures': self.signatures}
        return transaction_all

    def set_transaction_data(self, transaction_data):
        """this just loads the transactions passively, no change"""
        self.transaction = transaction_data['transaction']
        self.signatures = transaction_data['signatures']
        return transaction_data

    def loadtransactionpassive(self, file):
        transactiondata = {}
        with open(file, "r") as readfile:
            # print("Now reading from ", file)
            trandata = json.load(readfile)
        self.transaction = trandata['transaction']
        self.signatures = trandata['signatures']
        return trandata

    def save_transaction_to_mempool(self, file=None):
        """dumps active transaction into a stated file or in mempool by default"""
        transaction_timestamp = self.transaction['timestamp']
        if not transaction_timestamp:
            transaction_timestamp = get_time_ms()
        if not file:
            file = f"{self.mempool}transaction-{self.transaction['type']}-{transaction_timestamp}.json"
        transaction_complete = self.get_transaction_complete()
        with open(file, "w") as writefile:
            json.dump(transaction_complete, writefile)
            print("Wrote transaction to ", file)
        return file

    def get_transaction_complete(self):
        transaction_all = {
            'transaction': self.transaction,
            'signatures': self.signatures
        }
        return transaction_all

    def sign_transaction(self, private_key_bytes, address):
        """this takes keybytes and not binary string and not base64 string"""
        msg = json.dumps(self.transaction).encode()
        signing_key = ecdsa.SigningKey.from_string(
            private_key_bytes, curve=ecdsa.SECP256k1)
        msgsignbytes = signing_key.sign(msg)
        msgsign = msgsignbytes.hex()
        self.signatures.append({'wallet_address': address, 'msgsign': msgsign})
        return msgsignbytes

    def verify_sign(self, sign_trans, public_key_bytes):
        """The pubkey above is in bytes form"""
        # sign_trans_bytes = base64.decodebytes(sign_trans.encode('utf-8'))
        sign_trans_bytes = bytes.fromhex(sign_trans)
        verifying_key = ecdsa.VerifyingKey.from_string(
            public_key_bytes, curve=ecdsa.SECP256k1)
        message = json.dumps(self.transaction).encode()
        return verifying_key.verify(sign_trans_bytes, message)

    def verifytransigns(self):
        # need to add later a check for addresses mentioned in the transaction (vary by type) and the signing ones
        try:
            validadds = self.get_valid_addresses()
            if validadds == False:
                return False
        except Exception as e:
            logger.error(e)
            return False
        addvaliditydict = {}
        for valadd in validadds:
            addvaliditydict[valadd] = False

        prodflag = 1
        for signature in self.signatures:
            signaddress = signature['wallet_address']
            addressvalidity = 0
            for valadd in validadds:
                if signaddress == valadd:  # the signature is of a relevant address for that transaction
                    addressvalidity = 1
            if not addressvalidity:
                print("Signature with address ", signaddress,
                      " is not relevant for this transaction.")
                continue
            msgsign = signature['msgsign']
            pubkey = get_public_key_from_address(signaddress)
            if pubkey is None:
                return False
    #		print("encoded pubkey from json file: ",pubkey)
            # here we decode the base64 form to get pubkeybytes
            pubkeybytes = bytes.fromhex(pubkey)
        #	print("decoded bytes of pubkey",pubkeybytes)
    #		print("now verifying ",msgsign)
            if not self.verify_sign(msgsign, pubkeybytes):
                print("Signature for address ", signaddress, " is invalid")
                prodflag = prodflag*0
                addvaliditydict[signaddress] = False  # making doubly sure
                return False
            else:
                # for a valid address the signature is found
                addvaliditydict[signaddress] = True
                prodflag = prodflag*1
        # if prodflag:
            # print("All provided signatures of the message valid; still need to check if all required ones are provided")
        #	return True
        # else:
            # print("Some of the provided signatures not valid")
        #	return False
        # now checking if signatures for all valid addresses are covered
        validsignspresent = 0
        for valadd in validadds:
            if addvaliditydict[valadd]:
                validsignspresent += 1
            else:
                print(
                    "Either couldn't find signature or found invalid signature for ", valadd)
            #	valaddsignpresent=valaddsignpresent*0;	#any one signaure not being present will throw an error
        if prodflag and validsignspresent >= len(validadds):
            # print("All provided signatures valid and all required signatures provided")
            return True
        else:
            print("Either some signatures invalid or some required ones missing")
            return False

    def mempoolpayment(self, sender, tokencode):
        #	if not mempool:
        mempool = self.mempool
        filenames = os.listdir(mempool)
        mppayment = 0
        for filename in filenames:
            fl = mempool+filename
        #	self.loadtransaction
            try:
                with open(fl, "r") as readfile:
                    trandata = json.load(readfile)['transaction']
            except:
                print('Invalid transaction')
                continue
            ttype = trandata['type']
            if ttype < 3:  # 0 is genesis, 1 is wallet creation, 2 is token creation
                continue
            if ttype == 5:  # unilateral transaction so will have only asset_1 number
                if sender == trandata['specific_data']['wallet1'] and trandata['specific_data']['asset1_code'] == tokencode:
                    mppayment += trandata['specific_data']['asset1_number']
            if ttype == 4:  # bilateral trasnaction so will have both aset_1 and asset_2 numbers
                if sender == trandata['specific_data']['wallet1'] and trandata['specific_data']['asset1_code'] == tokencode:
                    mppayment += trandata['specific_data']['asset1_number']
                if sender == trandata['specific_data']['wallet2'] and trandata['specific_data']['asset2_code'] == tokencode:
                    mppayment += trandata['specific_data']['asset2_number']

        #	need to incorporate the fee as well in future
        return mppayment

    def econvalidator(self, cur=None):
        # start with all holdings of the wallets involved and add validated transactions from mempool
        # from mempool only include transactions that reduce balance and not those that increase
        # check if the sender has enough balance to spend
        self.validity = 0

        if not validate_transaction_fee(self.transaction, self.signatures, cur=cur):
            logger.error("Fee validation failed")
            return False
        fee_token_code = self.transaction['currency']
        if 'fee' in self.transaction:
            fee = self.transaction['fee']
        else:
            fee = 0

        if self.transaction['type'] == TRANSACTION_WALLET_CREATION:
            custodian = self.transaction['specific_data']['custodian_wallet']
            walletaddress = self.transaction['specific_data']['wallet_address']
            if not is_custodian_wallet(custodian, cur=cur):
                logger.warn('Invalid custodian wallet')
                self.validity = 0
            else:
                # print("Valid custodian address")
                #                if self.transaction['specific_data']['specific_data']['linked_wallet']:  #linked wallet
                if 'linked_wallet' in self.transaction['specific_data']['specific_data']:
                    linkedwalletstatus = self.transaction['specific_data']['specific_data']['linked_wallet']
                else:
                    linkedwalletstatus = False
                if linkedwalletstatus:
                    parentwalletaddress = self.transaction['specific_data']['specific_data']['parentaddress']
                    if custodian == parentwalletaddress:
                        self.validity = 1  # linking a new wallet is signed by existing wallet itself
                    else:
                        self.validity = 0  # other custodian cannot sign someone's linked wallet address
                else:   # this is a new wallet and person
                    if is_wallet_valid(walletaddress, cur=cur) and not is_smart_contract(walletaddress, cur=cur):
                        print("Wallet with address",
                              walletaddress, " already exists.")
                        self.validity = 0
                    else:
                        self.validity = 1

    #	self.validity=0
        # token addition transaction
        if self.transaction['type'] == TRANSACTION_TOKEN_CREATION:
            firstowner = self.transaction['specific_data']['first_owner']
            custodian = self.transaction['specific_data']['custodian']
            fovalidity = False
            custvalidity = False

            is_token_update = self.transaction['specific_data'].get('token_update', False)
            if not is_token_update:
                if firstowner:
                    if is_wallet_valid(firstowner, cur=cur):
                        # print("Valid first owner")
                        fovalidity = True
                    else:
                        fovalidity = False
                else:   # there is no first owner, transaction to create token only
                    if self.transaction['specific_data']['amount_created']:
                        print(
                            "Amount created cannot be non-zero if there is no first owner.")
                        fovalidity = False  # amount cannot be non-zero if no first owner
                    else:
                        fovalidity = True
                if is_wallet_valid(custodian, cur=cur):
                    # print("Valid custodian")
                    custvalidity = True
                if not fovalidity:
                    print("No first owner address found")
                #	self.transaction['valid']=0
                    self.validity = 0
                if not custvalidity:
                    print("No custodian address found")
                    self.validity = 0
                if fovalidity and custvalidity:
                # print("Valid first owner and custodian")
                #	self.transaction['valid']=1
                #   now checking for instances where more tokens are added for an existing tokencode
                   self.validity = 1
                if 'tokencode' in self.transaction['specific_data']:
                    tcode = self.transaction['specific_data']['tokencode']
                    if tcode and tcode != "0" and tcode != "" and tcode != "string":
                        if is_token_valid(self.transaction['specific_data']['tokencode'], cur=cur):
                            if is_nft(tcode,cur):
                                logger.error("this is an nft, cant be created further")
                                return False
                            existing_custodian = get_custodian_from_token(
                                self.transaction['specific_data']['tokencode'],cur = cur)
                            if custodian == existing_custodian:
                                self.validity = 1  # tokencode exists and is run by the given custodian
                            else:
                                print(
                                    "The custodian for that token is someone else.")
                                self.validity = 0
                        else:

                            # print(
                            #     "Tokencode provided does not exist. Will append as new one.")
                            #if nft then amount cant be more than one
                            if self.transaction['specific_data']['tokentype'] == TOKEN_NFT and self.transaction['specific_data']['amount_created'] > 1:
                                logger.error("This is an nft token type, Amount cant be grater than one")
                                return False
                            self.validity = 1  # tokencode is provided by user
                       

                    else:
                        # print(
                        #     "Tokencode provided does not exist. Will append as new one.")
                        self.validity = 1  # tokencode is provided by user
            else: 
            
                if is_wallet_valid(custodian, cur=cur):
                    # print("Valid custodian")
                    custvalidity = True 
                if not custvalidity:
                    print("No custodian address found")
                    self.validity = 0
                if 'tokencode' in self.transaction['specific_data']:
                    tcode = self.transaction['specific_data']['tokencode']
                    if tcode and tcode != "0" and tcode != "" and tcode != "string":
                        token_attributes_dump = fetch_token(tcode,cur = cur)
                        token_attributes = json.loads(token_attributes_dump)

                        is_editable = token_attributes.get("editable",False)

                        if not is_editable:
                            self.validity = 0
                        else:
                            if is_token_valid(self.transaction['specific_data']['tokencode'], cur=cur):
                                existing_custodian = get_custodian_from_token(
                                    self.transaction['specific_data']['tokencode'],cur = cur)
                                if custodian == existing_custodian:
                                    self.validity = 1  # tokencode exists and is run by the given custodian
                                else:
                                    print(
                                        "The custodian for that token is someone else.")
                                    self.validity = 0
                            else:
                                # print(
                                #     "Tokencode provided does not exist. Will append as new one.")
                                self.validity = 1 
                        

        if self.transaction['type'] == TRANSACTION_SMART_CONTRACT:
            self.validity = 1
            for wallet in self.transaction['specific_data']['signers']:
                if not is_wallet_valid(wallet, cur=cur):
                    self.validity = 0
            if 'participants' in self.transaction['specific_data']['params']:
                for wallet in self.transaction['specific_data']['params']['participants']:
                    if not is_wallet_valid(wallet, cur=cur):
                        self.validity = 0
            if 'value' in self.transaction['specific_data']['params']:
                for value in self.transaction['specific_data']['params']['value']:
                    print(value)
                    if not is_token_valid(value['token_code'], cur=cur):
                        self.validity = 0
                        break
                    sender_balance = get_wallet_token_balance_tm(
                        self.transaction['specific_data']['signers'][0], value['token_code'], cur)
                    if value['amount'] > sender_balance:
                        self.validity = 0
                        break
    #	self.validity=0
        if self.transaction['type'] == TRANSACTION_TWO_WAY_TRANSFER or self.transaction['type'] == TRANSACTION_ONE_WAY_TRANSFER:
            ttype = self.transaction['type']
            startingbalance1 = 0
            startingbalance2 = 0
            wallet2 = self.transaction['specific_data']['wallet2']
            sender1 = self.transaction['specific_data']['wallet1']
            sender2 =  wallet2 if wallet2 else self.get_sender2()
            tokencode1 = self.transaction['specific_data']['asset1_code']
            # token1mp = self.mempoolpayment(sender1, tokencode1)
            # token1amt = max(
            #     self.transaction['specific_data']['asset1_number'], token1mp)
            token1amt = self.transaction['specific_data']['asset1_number']
            sender1valid = False
            sender2valid = False

            if (
                self.transaction['specific_data']['asset1_number'] < 0
                or self.transaction['specific_data']['asset2_number'] < 0
            ):
                logger.warn('Token quantity cannot be negative')
                self.validity = 0
                return False

            # for ttype=5, there is no tokencode for asset2 since it is off-chain, there is no amount either
            if ttype == 4:  # some attributes of transaction apply only for bilateral transfer and not unilateral
                #	startingbalance2=0;
                tokencode2 = self.transaction['specific_data']['asset2_code']
                # token2mp = self.mempoolpayment(sender2, tokencode2)
                # token2amt = max(
                #     self.transaction['specific_data']['asset2_number'], token2mp)
                token2amt = self.transaction['specific_data']['asset2_number']

            # address validity applies to both senders in ttype 4 and 5; since sender2 is still receiving tokens

            sender1valid = is_wallet_valid(sender1, cur=cur)
            #TODO attach 2 sigs present validation with sender2 == None
            sender2valid = is_wallet_valid(sender2, cur=cur) or (
                sender2 == Configuration.config("ZERO_ADDRESS") and ttype == 5) 
            if not sender1valid:
                print("Invalid sender1 wallet")
            #	self.transaction['valid']=0
                self.validity = 0
            #	return False
            if not sender2valid:
                print("Invalid sender2 wallet")
            #	self.transaction['valid']=0
                self.validity = 0
            #	return False

            # tokenvalidity applies for both senders only in ttype 4
            token1valid = False
            if ttype == 4:
                # by keeping it here, we ensure that no code refers to token2valid for type5
                token2valid = False
            token1valid = is_token_valid(tokencode1, cur=cur)
            token2valid = ttype == 4 and is_token_valid(tokencode2, cur=cur)
            if not token1valid:
                print("Invalid asset1 code")
                self.validity = 0
            if ttype == 4 and not token2valid:
                print("Invalid asset1 code")
                self.validity = 0
            if ttype == 4 and token1valid and token2valid:
                print("Valid tokens")
                self.validity = 1
            else:  # this is ttype=5
                if token1valid:
                    print("Valid tokens")
                    self.validity = 1

            if self.validity == 0 or not sender1valid or not sender2valid:
                print("Transaction not valid due to invalid tokens or addresses")
                return False

            # resetting to check the balances being sufficient, in futures, make different functions
            self.validity = 0

            startingbalance1 = get_wallet_token_balance_tm(
                sender1, tokencode1, cur)
            if ttype == 4:
                startingbalance2 = get_wallet_token_balance_tm(
                    sender2, tokencode2, cur)

            if ttype == 5:
                # If fee_payer is present, fee is deducted before from fee_payer
                if 'fee_payer' in self.transaction:
                    token1_balance_validity = token1amt < startingbalance1
                else:
                    #if token being transfered and fee token is same, calculate together
                    if tokencode1 == fee_token_code:
                        if token1amt + fee <= startingbalance1:
                            print(
                                "Valid economics of transaction. Changing economic validity value to 1")
                            self.validity = 1
                    else:
                        #check for fee and token1 balances seperately
                        fee_token_balance = get_wallet_token_balance_tm(
                            sender1, fee_token_code, cur=cur)
                        if fee <= fee_token_balance:
                            if token1amt <= startingbalance1:
                                print(
                                    "Valid economics of transaction. Changing economic validity value to 1")
                                self.validity = 1
            if ttype == 4:
                token1_balance_validity = False
                token2_balance_validity = False
                # If fee_payer is present, fee is deducted before from fee_payer
                if 'fee_payer' in self.transaction:
                    token1_balance_validity = token1amt <= startingbalance1
                    token2_balance_validity = token2amt <= startingbalance2
                else:
                    #token1 balance check
                    if tokencode1 == fee_token_code:
                        if token1amt + math.ceil(fee/2) <= startingbalance1:
                            print(
                                "Valid economics of transaction. Changing economic validity value to 1")
                            token1_balance_validity = True
                    else:
                        #check for fee and token1 balances seperately
                        fee_token_balance = get_wallet_token_balance_tm(
                            sender1, fee_token_code, cur=cur)
                        if math.ceil(fee/2) <= fee_token_balance:
                            if token1amt <= startingbalance1:
                                print(
                                    "Valid economics of transaction. Changing economic validity value to 1")
                                token1_balance_validity = True
                    #token2 balance check
                    if tokencode2 == fee_token_code:
                        if token2amt + math.ceil(fee/2) <= startingbalance2:
                            print(
                                "Valid economics of transaction. Changing economic validity value to 1")
                            token2_balance_validity = True
                    else:
                        #check for fee and token2 balances seperately
                        fee_token_balance = get_wallet_token_balance_tm(
                            sender2, fee_token_code, cur=cur)
                        if math.ceil(fee/2) <= fee_token_balance:
                            if token2amt <= startingbalance2:
                                print(
                                    "Valid economics of transaction. Changing economic validity value to 1")
                                token2_balance_validity = True

                if token1_balance_validity and token2_balance_validity:
                    self.validity = 1

        # score change transaction
        if self.transaction['type'] == TRANSACTION_TRUST_SCORE_CHANGE:
            ttype = self.transaction['type']
        #    personid1 = self.transaction['specific_data']['personid1']
        #    personid2 = self.transaction['specific_data']['personid2']
            wallet1 = self.transaction['specific_data']['address1']
            wallet2 = self.transaction['specific_data']['address2']
            wallet1valid = False
            wallet2valid = False

            wallet1valid = is_wallet_valid(wallet1, cur=cur)
            wallet2valid = is_wallet_valid(wallet2, cur=cur)
            if not wallet1valid or not wallet2valid:
                print("One of the wallets is invalid")
                self.validity = 0
            else:
                #    if get_pid_from_wallet(wallet1) != personid1 or get_pid_from_wallet(wallet2) != personid2:
                pid_1 = get_pid_from_wallet(wallet1, cur=cur)
                pid_2 = get_pid_from_wallet(wallet2, cur=cur)
                if not pid_1 or not pid_2:
                    print(
                        "One of the wallet addresses does not have a valid associated personids.")
                    self.validity = 0
                elif pid_1 == pid_2:
                    logger.warn('src and dst person ids cannot be same')
                    self.validity = 0
                else:
                    if self.transaction['specific_data']['new_score'] < -1000000 or self.transaction['specific_data']['new_score'] > 1000000:
                        print("New_score is out of valid range.")
                        self.validity = 0
                    else:
                        self.validity = 1

        if self.transaction['type'] == TRANSACTION_MINER_ADDITION:
            # No checks for fee in the beginning
            if not is_wallet_valid(self.transaction['specific_data']['wallet_address'], cur=cur, check_sc=False):
                print("Miner wallet not in chain")
                self.validity = 0
            else:
                self.validity = 1
        if self.transaction['type'] == TRANSACTION_SC_UPDATE:
            self.validity = 1

        if self.validity == 1:
            return True
        else:
            return False  # this includes the case where valid=-1 i.e. yet to be validated

    def contract_validate(self):
        transaction = self.transaction
        specific_data = transaction['specific_data']
        funct_called = specific_data["function"]
        if funct_called == "setup":
            return True
        funct_name = "validate"
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        contract = get_contract_from_address(cur, specific_data['address'])

        try:
            module = importlib.import_module(
                ".core.contracts." + contract['name'], package="app")
            sc_class = getattr(module, contract['name'])
            sc_instance = sc_class(specific_data['address'])
            funct = getattr(sc_instance, funct_name)
            fetchRepository = FetchRepository(cur)
            funct(specific_data, fetchRepository)
        except TypeError as e:
            logger.warn(f"Validate method not implemented for {sc_class}")
            con.close()
            return True
        except AttributeError as e:
            logger.warn(f"Validate method not implemented for {sc_class}")
            con.close()
            return True
        except ContractValidationError as e:
            logger.error(f"Contract validation failed {e}")
            con.close()
            return False
        except Exception as e:
            logger.error(f"{type(e)}")
            logger.error(f"Error validating the contract call {e}")
            con.close()
            return False

        con.close()

        return True
#	def legalvalidator(self):
        # check the token restrictions on ownertype and check the type of the recipient

    def get_sender2(self):
        transaction_data = self.transaction["specific_data"]
        transaction_signer = self.signatures
        sender1 = transaction_data["wallet1"]
        if transaction_data['wallet2'] is not None:
            return transaction_data['wallet2']
        else:
            # if transaction_signer[0]["wallet_address"] == sender1:
            #     return transaction_signer[1]["wallet_address"]
            # else:
            #     return transaction_signer[0]["wallet_address"]
            fee_payer = self.get_fee_payer()
            for sig in transaction_signer:
                if (sig["wallet_address"] != sender1) and (sig["wallet_address"] != fee_payer):
                    return sig["wallet_address"]

                    
    def get_fee_payer(self):
        if 'fee_payer' in self.transaction:
            return self.transaction['fee_payer']
        return None    

def get_public_key_from_address(address, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    wallet_cursor = cur.execute(
        'SELECT wallet_public FROM wallets WHERE wallet_address=?', (address, ))
    public_key = wallet_cursor.fetchone()
    if cursor_opened:
        con.close()
    if public_key is None:
        return None
    return public_key[0]


def is_token_valid(token_code, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    token_cursor = cur.execute(
        'SELECT tokencode FROM tokens WHERE tokencode=?', (token_code, ))
    token = token_cursor.fetchone()
    if cursor_opened:
        con.close()
    if token is None:
        return False
    return True

def fetch_token(token_code, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    token_cursor = cur.execute(
        'SELECT token_attributes FROM tokens WHERE tokencode=?', (token_code, ))
    token = token_cursor.fetchone()
    if cursor_opened:
        con.close()
    if token is None:
        return None
    return token[0]

def fetch_token_type(token_code, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    token_cursor = cur.execute(
        'SELECT tokentype FROM tokens WHERE tokencode=?', (token_code, ))
    token = token_cursor.fetchone()
    if cursor_opened:
        con.close()
    if token is None:
        return None
    return token[0]

def is_wallet_valid(address, cur=None, check_sc=True):
    if check_sc:
        if is_smart_contract(address, cur=cur):
            return True
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False

    wallet_cursor = cur.execute(
        'SELECT wallet_public FROM wallets WHERE wallet_address=?', (address, ))
    wallet = wallet_cursor.fetchone()
    if cursor_opened:
        con.close()
    if wallet is None:
        return False

    return True


def is_custodian_wallet(address, cur=None):
    """
        If address in [initial foundation addresses], return True
        Check if address is in custodian DAO return True
        Return false otherwise
    """
    custodian_wallet_list = json.loads(
        Configuration.config('CUSTODIAN_WALLET_LIST'))
    if address in custodian_wallet_list:
        return True

    custodian_dao_pid = get_person_id_for_wallet_address(CUSTODIAN_DAO_ADDRESS)
    wallet_pid = get_person_id_for_wallet_address(address)
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    pid_cursor = cur.execute(
        'SELECT count(*) FROM dao_membership WHERE dao_person_id=? and member_person_id=?', (custodian_dao_pid, wallet_pid))
    pid = pid_cursor.fetchone()
    is_valid_custodian = pid[0] != 0
    if cursor_opened:
        con.close()

    return is_valid_custodian


def get_wallets_from_pid(personidinput, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    wallet_cursor = cur.execute(
        'SELECT wallet_id FROM person_wallet WHERE person_id=?', (personidinput, )).fetchall()
    if cursor_opened:
        con.close()
    if wallet_cursor is None:
        return False
    wallets = [dict(wlt) for wlt in wallet_cursor]
    return wallets


def get_pid_from_wallet(walletaddinput, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    pid_cursor = cur.execute(
        'SELECT person_id FROM person_wallet WHERE wallet_id=?', (walletaddinput, ))
    pid = pid_cursor.fetchone()
    if cursor_opened:
        con.close()
    if pid is None:
        return False
    return pid[0]


def get_custodian_from_token(token_code, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    token_cursor = cur.execute(
        'SELECT custodian FROM tokens WHERE tokencode=?', (token_code, ))
    custodian = token_cursor.fetchone()
    if cursor_opened:
        con.close()
    if custodian is None:
        return False
    return custodian[0]


def get_miner_count_person_id(person_id, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    token_cursor = cur.execute(
        '''
        select count(*) from miners
        where wallet_address in
        (select wallet_id from person_wallet
            where person_id = ?)
        ''', (person_id, ))
    result = token_cursor.fetchone()
    if cursor_opened:
        con.close()
    if result is None:
        return 0
    return result[0]


def get_sc_validadds(transaction, cur=None):
    validadds = []
    funct = transaction['specific_data']['function']
    address = transaction['specific_data']['address']
    if funct == "setup":  # the sc is not yet set up
        validadds.append(transaction['specific_data']['params']['creator'])
        return validadds
    if not address:
        print("Invalid call to a function of a contract yet to be set up.")
        return [-1]
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False
    signatories = cur.execute(
        'SELECT signatories FROM contracts WHERE address=?', (address, )).fetchone()
    if cursor_opened:
        con.close()
    if signatories is None:
        print("Contract does not exist.")
        return [-1]
    functsignmap = json.loads(signatories[0])
    if funct in functsignmap:  # function is allowed to be called
        # checking if stated signer is in allowed list
        for signer in (transaction['specific_data']['signers']):
            if not functsignmap[funct] or signer in functsignmap[funct]:
                validadds.append(signer)
            # a function may allow anyone to call or the signer may be present in the dictionary funcsignmap
        return validadds
    else:
        print("Either function is not valid or it cannot be called in a transaction.")
        return [-1]


def get_valid_addresses(transaction, address = None, cur=None):
    """Get valid signature addresses for a transaction"""
    transaction_type = transaction['type']
    valid_addresses = []
    if transaction_type == TRANSACTION_WALLET_CREATION:  # Custodian needs to sign
        valid_addresses.append(
            transaction['specific_data']['custodian_wallet'])
    if transaction_type == TRANSACTION_TOKEN_CREATION:    # Custodian needs to sign
        valid_addresses.append(transaction['specific_data']['custodian'])
    if transaction_type == TRANSACTION_SMART_CONTRACT:
        valid_addresses = get_sc_validadds(transaction, cur=cur)
    if transaction_type == TRANSACTION_TWO_WAY_TRANSFER:  # Both senders need to sign
        if transaction['specific_data']['wallet1'] == transaction['specific_data']['wallet2']:
            raise Exception('Both senders cannot be same')
        valid_addresses.append(transaction['specific_data']['wallet1'])
        
        if transaction['specific_data']['wallet2'] is not None:
            valid_addresses.append(transaction['specific_data']['wallet2'])
        elif address is not None:
            valid_addresses.append(address)
            
    if transaction_type == TRANSACTION_ONE_WAY_TRANSFER:  # Only sender1 is needed to sign
        valid_addresses.append(transaction['specific_data']['wallet1'])
    if transaction_type == TRANSACTION_TRUST_SCORE_CHANGE:
        # Only address1 is added, not address2
        valid_addresses.append(transaction['specific_data']['address1'])
    if transaction_type == TRANSACTION_MINER_ADDITION:
        valid_addresses.append(transaction['specific_data']['wallet_address'])
    return valid_addresses


def get_wallet_token_balance_tm(wallet_address, token_code, cur=None):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False

    balance = get_wallet_token_balance(cur, wallet_address, token_code)
    # balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
    #     'address': wallet_address, 'tokencode': token_code})
    # balance_row = balance_cursor.fetchone()
    # balance = balance_row[0] if balance_row is not None else 0
    if cursor_opened:
        con.close()
    return balance


def is_smart_contract(address, cur=None):
    if not address.startswith('ct'):
        return False
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False

    sc_cursor = cur.execute(
        'SELECT COUNT (*) FROM contracts WHERE address=?', (address, ))
    sc_id = sc_cursor.fetchone()
    if cursor_opened:
        con.close()
    if sc_id is None:
        return False
    else:
        return True


def __str__(self):
    return str(self.get_transaction_complete())

def is_nft(token_code,cur):
    token_type = fetch_token_type(token_code,cur = cur)
    is_nft =  token_type == TOKEN_NFT
    return is_nft

def validate_transaction_fee(transaction, signatures, cur):
    if cur is None:
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        cursor_opened = True
    else:
        cursor_opened = False

    fee_tokens = [NEWRL_TOKEN_CODE, NUSD_TOKEN_CODE]
    fee_token_code = transaction['currency']
    if not fee_token_code in fee_tokens:
        logger.info("Provided fee currency is not allowed")
        return False

    if 'fee' in transaction:
        fee = transaction['fee']
    else:
        fee = 0

    if 'is_child_txn' in transaction:
        is_child_sc = transaction['is_child_txn']
        if is_child_sc:
            return True

    if transaction['type'] in [TRANSACTION_MINER_ADDITION, TRANSACTION_SC_UPDATE]:
        return True

    if fee_token_code == NEWRL_TOKEN_CODE:
        if fee < NEWRL_TOKEN_MULTIPLIER:
            logger.info(f"Not enough fee provided: {fee}")

        if 'fee_payer' in transaction:
            found_fee_payer = False
            for sign in signatures:
                if sign['wallet_address'] == transaction['fee_payer']:
                    found_fee_payer = True
                    break
            if not found_fee_payer:
                logger.info(f"Transaction includes fee_payer but not signed by fee_payer")
                return False
            payees = [transaction['fee_payer']]
        else:
            payees = get_valid_addresses(transaction, cur=cur)
        for payee in payees:
            balance = get_wallet_token_balance(cur, payee, fee_token_code)
            fee_to_charge = math.ceil(fee / len(payees))
            if balance < fee_to_charge:
                logger.info(
                    f"Payee {payee} does not have enough balance. Required:{fee_to_charge} Available:{balance}")
                return False
    else:
        logger.info(f"Fee payment currency not allowed")
        return False
    if cursor_opened:
        con.close()
    return True
