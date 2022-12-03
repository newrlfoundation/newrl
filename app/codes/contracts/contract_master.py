# class to create smart contract master template
#import codecs
#from marshal import loads
#from subprocess import call
#import uuid
#import ecdsa
#from Crypto.Hash import keccak
#import os
from abc import abstractmethod
import abc
import json
import datetime
import time
import sqlite3
from app.codes.cache import DB_CACHE

from app.codes.helpers.TransactionCreator import TransactionCreator
#import hashlib

from ...constants import NEWRL_DB
from ..db_updater import *


class ContractMaster():
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class
    def __init__(self, template, version, contractaddress=None):
        self.address=contractaddress    #this is for instances of this class created for tx creation and other non-chain work
        self.type=1
        self.template=template
        self.new_contract = False
        if contractaddress:     #as in this is an existing contract
            
            params = self.loadcontract(contractaddress)  #this will populate the params for a given instance of the contract
            
            if not params:
                self.new_contract = True
                self.contractparams = self.get_default_contract_params(
                    template, version)
        else:   #either no contractaddress provided or new adddress not in db
            self.address = create_contract_address()
            self.contractparams=self.get_default_contract_params(template, version)
            self.new_contract = True
            # no pre-set address, need to create a new one

    def setup(self, callparams, fetchRepository):
        #this is called by a tx type 3 signed by the creator, it calls the function setp with parameters as params
        #setup implies a transaction for contract address creation

        if not self.new_contract:
            raise Exception("This exists a contract already in the database with same address")

        contractparams= input_to_dict(callparams)

        if not (contractparams['status']==0 or contractparams['status'] is None):
            raise Exception("Contract status provided is not valid. Should be 0 or None for contracts that aren't setup")
        
        # if contractparams['status']==-1:
        #     print("Contract is already terminated, cannot setup. Exiting.")
        #     return False
        # if contractparams['status']==2:
        #     print("Contract already deployed, cannot setup. Exiting.")
        #     return False
        # if contractparams['status']==3:
        #     print("Contract already expired, cannot setup. Exiting.")
        #     return False
        # if contractparams['status']==1:
        #     print("Contract already setup, cannot setup again. Exiting.")
        #     return False
        #add other codes here if in future 4 onwards are used for specifying other contract states.
        
        if contractparams['name']!=self.template:
            print("Mismatch in contractname. Not creating a new contract.")
            return False
        #    if contractparams['version']!=self.version:
        #        print("Mismatch in contract version. Not creating a new contract.")
        #        return False
        contractparams['status']=1
        #status convention: 0 or None is not setup yet, 1 is setup but not deployed, 2 is setup and deployed, 3 is expired and -1 is terminated
        
        # now we need to update the contract parameters in SC database; for now we are appending to the allcontracts.json
        contractparams['ts_init'] = time.mktime(datetime.datetime.now().timetuple())
        #contractparams['ts_init']=str(datetime.datetime.now()
        contractparams['address']= self.address
        self.contractparams=contractparams
        #########
        #code to append contractdata into allcontracts db
        sdestr=0 if not contractparams['selfdestruct'] else int(contractparams['selfdestruct'])
        cstatus = 0 if not contractparams['status'] else int(contractparams['status'])
        cspecs=json.dumps(contractparams['contractspecs'])
        legpars=json.dumps(contractparams['legalparams'])
        signstr=json.dumps(contractparams['signatories'])
        oraclestr = json.dumps(contractparams['oracleids'])
        qparams=((self.address).strip('\"'),
                contractparams['creator'],
                contractparams['ts_init'],
                contractparams['name'],
                contractparams['version'],
                contractparams['actmode'],
                cstatus,
                contractparams['next_act_ts'],
                signstr,
                contractparams['parent'],
                oraclestr,
                sdestr,
                cspecs,
                legpars
                )

        contract_data = {
            "address": (self.address).strip('\"'),
            "creator": contractparams['creator'],
            "ts_init": contractparams['ts_init'],
            "name": contractparams['name'],
            "version": contractparams['version'],
            "actmode": contractparams['actmode'],
            "status": cstatus,
            "next_act_ts":  contractparams['next_act_ts'],
            "signatories": signstr,
            "parent": contractparams['parent'],
            "oracleids": oraclestr,
            "selfdestruct": sdestr,
            "contractspecs": cspecs,
            "legalparams": legpars
        }
        '''txn type 8 (sc-private state update)'''
        sc_state_proposal1_data = {
            "operation": "save",
            "table_name": "contracts",
            "sc_address": self.address,
            "data": contract_data
        }

        transaction_creator = TransactionCreator()
        add_contract_proposal = transaction_creator.transaction_type_8(
            sc_state_proposal1_data)

        return [add_contract_proposal]
    def loadcontract(self, cur, contractaddress):
        #this loads the contract from the state db
        #it should take as input contractaddress and output the contractparams as they are in the db as of the time of calling it
        #the output will populate self.contractparams to be used by other functions
        if contractaddress in DB_CACHE['contract_params']:
            self.contractparams = DB_CACHE['contract_params'][contractaddress]
        else:
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            contract_cursor = cur.execute('SELECT * FROM contracts WHERE address = :address', {
                        'address': contractaddress})
            contract_row = contract_cursor.fetchone()
            con.close()
            if not contract_row:
                self.new_contract = True
                return False

            self.contractparams = {k[0]: v for k, v in list(zip(contract_cursor.description, contract_row))}
            DB_CACHE['contract_params'][contractaddress] = self.contractparams
        self.contractparams['contractspecs']=json.loads(self.contractparams['contractspecs'])
        self.contractparams['legalparams']=json.loads(self.contractparams['legalparams'])
        self.contractparams['signatories']=json.loads(self.contractparams['signatories'])
        self.contractparams['oracleids'] = json.loads(self.contractparams['oracleids'])
        self.new_contract = False
        print("Loaded the contract with following data: \n",self.contractparams)
        return self.contractparams
        
    def deploy(self, cur, callparamsip):
        # carries out the SC execution steps upon instruction from a transaction - during updater run, post block inclusion
        callparams= input_to_dict(callparamsip)
        if self.contractparams['status'] != 1:    #the contract is not setup, i.e. is either yet to be setup, already deployed or terminated
            print("The contract is not in the post-setup stage. Exiting without deploying.")
            return False
        else:
            if self.sendervalid(callparams['sender'], self.deploy.__name__):
                self.contractparams['status'] = 2     # changed from 1 (setup done) to 2 (deployed and live)
                cur.execute(f'''UPDATE contracts SET status=? WHERE address=?''', (self.contractparams['status'], self.address))
                print("Deployed smart contract - ",self.template,"with address ",self.address)
                self.updateondeploy(cur)
                return True
            else:
                print("Sender not valid or not allowed this function call.")
                return False

    def sendervalid(self, senderaddress, function):
        sendervalidity = False
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        if 'approved_senders' not in cspecs:
            return True
        for appr_sender in self.contractparams['contractspecs']['approved_senders']:
            if senderaddress == appr_sender['address']:
                if appr_sender['allowed'] == 'all' or function in appr_sender['allowed']:
                    sendervalidity = True
        return sendervalidity

    def get_default_contract_params(self,template,version):
        contractparams = {}
        contractparams['creator']=""
        contractparams['ts_init']=0
        contractparams['name']=template
        contractparams['version']=version
        contractparams['actmode']="hybrid"
        contractparams['status']=0
        contractparams['next_act_ts']=0
        contractparams['signatories']=[]
        contractparams['parent']=""
        contractparams['oracleids']=[]
        contractparams['contractspecs']={}
        contractparams['legalparams']={}  
        return contractparams       





