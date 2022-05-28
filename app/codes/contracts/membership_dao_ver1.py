from .dao_main_template import DaoMainTemplate
from ..db_updater import *

class membership_dao_ver1(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None):
        self.template= 'membership_dao_ver1'
        self.version='1.0.0'
        self.dao_type=1
        super().__init__(contractaddress)
