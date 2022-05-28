# class to create smart contract for creating stablecoins on Newrl
from .contract_master import ContractMaster
from ..db_updater import *

class nusd1(ContractMaster):
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self,contractaddress=None):
        self.template= "nusd1"
        self.version=""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateondeploy(self, cur):
        if 'legaldochash' in self.contractparams['legalparams']:
            legaldochash = self.contractparams['legalparams']['legaldochash']
        else:
            legaldochash = None
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        tokendata={"tokencode": cspecs['tokencode'],
                   "tokenname": cspecs['tokenname'],
                   "tokentype": 1,
                   "tokenattributes": {"fiat_currency":"USD", "sc_address": self.address},
                   "first_owner": None,
                   "custodian": self.address,
                   "legaldochash": legaldochash,
                   "amount_created": None,
                   "disallowed": [],
                   "tokendecimal":2,
                   "sc_flag": True
                   }
        add_token(cur, tokendata, self.contractparams['parent'])

    def send_nusd_token(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        recipient_address = callparams['recipient_address']
        sender = callparams['sender']
        value = callparams['value']
        print("callparams are ",callparams)
        try:
            value = float(value)
        except:
            print("Can't read value as a valid number.")
            return False
        if not is_wallet_valid(cur, recipient_address):
            print("Recipient address not valid.")
            return False
        if not self.sendervalid(sender, self.sendervalid.__name__):
            print("Sender is not in the approved senders list.")
            return False
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        tokendata={"tokencode": cspecs['tokencode'],
                   "first_owner": recipient_address,
                   "custodian": self.address,
                   "amount_created": int(value*100),
                   "tokendecimal":2
                   }
        add_token(cur, tokendata)
        
    def burn_nusd_token(self,sender_address, value):
        pass