from .dao_main_template import DaoMainTemplate
from ..db_updater import *

class token_dao(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None):
        self.template= 'token_dao'
        self.version='1.0.0'
        self.dao_type=2
        # dao_type=2 is for token based DAO and 1 is for membership DAO
        super().__init__(contractaddress)
