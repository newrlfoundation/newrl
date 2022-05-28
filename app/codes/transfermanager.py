"""Inter wallet token transfer manager"""
from .transactionmanager import Transactionmanager


class Transfermanager(Transactionmanager):
    """Wallet-Wallet token transfer helper"""
    def __init__(self, transfer_data):
        Transactionmanager.__init__(self)
        self.transaction = transfer_data['transaction']
        self.fulltrandata = transfer_data

    def loadandcreate(self, transfer_data=None):
        """Create a transfermanager from transfer data"""
        tdatawithcode = self.transactioncreator(self.fulltrandata)
        return tdatawithcode
