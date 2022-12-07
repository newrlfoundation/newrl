import logging
from abc import ABC

from .dao_main_template import DaoMainTemplate
from ..clock.global_time import get_corrected_time_ms
from ..db.db_updater import *
import math

from ..helpers.FetchRespository import FetchRepository
from app.core.blockchain.TransactionCreator import TransactionCreator


class ConfigurationManager(DaoMainTemplate, ABC):
    codehash=""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, contractaddress=None):
        self.template= 'ConfigurationManager'
        self.version='1.0.0'
        self.dao_type=1
        # dao_type=2 is for token based DAO and 1 is for membership DAO
        super().__init__(contractaddress)

    def change_config(self,callparamsip,repo: FetchRepository):
        trxn=[]
        callparams = input_to_dict(callparamsip)
        configArray=callparams['config']
        for i in configArray:
            config_data = repo.select_Query('property_key,property_value,is_editable').\
                add_table_name('configuration').\
                where_clause('property_key', i['property_key'],1).\
                execute_query_single_result({"property_key": i['property_key']})
            if config_data is None:
                logging.error(f"No property key found for {i['property_key']}")
                return trxn
            else:
                logging.info(f"Property value change from  {config_data[1]}, {i['property_value']}")
                sc_state_proposal1_data = {
                    "operation": "update",
                    "table_name": "configuration",
                    "sc_address": self.address,
                    "data": {
                        "property_value": i['property_value'],
                        "address": self.address,
                        "last_updated": get_corrected_time_ms()
                    },
                    "unique_column": "property_key",
                    "unique_value": i['property_key']
                }
                transaction_creator = TransactionCreator()
                txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                trxn.append(txtype1)

        return trxn

    def add_config(self,callparamsip,repo: FetchRepository):
        trxn=[]
        callparams = input_to_dict(callparamsip)
        configArray=callparams['config']
        for i in configArray:
            config_data = repo.select_Query('property_key,property_value,is_editable').\
                add_table_name('configuration').\
                where_clause('property_key', i['property_key'],1).\
                execute_query_single_result({"property_key": i['property_key']})
            if config_data is not None:
                logging.error(f"Property key already exists for {i['property_key']}")
                return trxn
            else:
                logging.info(f"Property value saved {i['property_value']}")
                sc_state_proposal1_data = {
                    "operation": "save",
                    "table_name": "configuration",
                    "sc_address": self.address,
                    "data": {
                        "property_key":i['property_key'],
                        "property_value": i['property_value'],
                        "address": self.address,
                        "last_updated": get_corrected_time_ms()
                    }
                }
                transaction_creator = TransactionCreator()
                txtype1 = transaction_creator.transaction_type_8(sc_state_proposal1_data)
                trxn.append(txtype1)

        return trxn


