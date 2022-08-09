import sqlite3

from app.constants import NEWRL_DB
from app.nvalues import *


class Configuration:
    __conf = {
        "ZERO_ADDRESS": '0x0000000000000000000000000000000000000000',
        "TREASURY_WALLET_ADDRESS": '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        "NETWORK_TRUST_MANAGER_WALLET": '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        "NETWORK_TRUST_MANAGER_PUBLIC": 'CcGRdIzGC0ODmycwg8xWWBHCb1zlSxftS0oXxh561riA/HrDCBucDPKHVuohzlAXibWej5ED82aMzyyGEIYo7g==',
        "NETWORK_TRUST_MANAGER_PID": 'pi10d84aa634ba8751804ca4e02134696a75ae3515',
        "ASQI_WALLET": '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        "ASQI_WALLET_PUBLIC": 'CcGRdIzGC0ODmycwg8xWWBHCb1zlSxftS0oXxh561riA/HrDCBucDPKHVuohzlAXibWej5ED82aMzyyGEIYo7g==',
        "FOUNDATION_WALLET": '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        "FOUNDATION_WALLET_PUBLIC": 'CcGRdIzGC0ODmycwg8xWWBHCb1zlSxftS0oXxh561riA/HrDCBucDPKHVuohzlAXibWej5ED82aMzyyGEIYo7g==',
        "SENTINEL_NODE_WALLET": '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        "SENTINEL_NODE_WALLET_PUBLIC": 'CcGRdIzGC0ODmycwg8xWWBHCb1zlSxftS0oXxh561riA/HrDCBucDPKHVuohzlAXibWej5ED82aMzyyGEIYo7g==',
        "DAO_MANAGER": 'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7',
        "ASQI_PID": 'pi10d84aa634ba8751804ca4e02134696a75ae3515'
    }
    __setters = ["ZERO_ADDRESS", "TREASURY_WALLET_ADDRESS", "NETWORK_TRUST_MANAGER_WALLET",
                 "NETWORK_TRUST_MANAGER_PUBLIC", "NETWORK_TRUST_MANAGER_PID", "ASQI_WALLET", "ASQI_WALLET_PUBLIC",
                 "FOUNDATION_WALLET", "FOUNDATION_WALLET_PUBLIC", "SENTINEL_NODE_WALLET", "SENTINEL_NODE_WALLET_PUBLIC",
                 "DAO_MANAGER","ASQI_PID"]

    @staticmethod
    def config(name):
        return Configuration.__conf[name]

    @staticmethod
    def set(name, value):
        if name in Configuration.__setters:
            Configuration.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")

    @staticmethod
    def init_values():
        Configuration.set("ZERO_ADDRESS", ZERO_ADDRESS)
        Configuration.set("TREASURY_WALLET_ADDRESS", TREASURY_WALLET_ADDRESS)
        Configuration.set("NETWORK_TRUST_MANAGER_WALLET", NETWORK_TRUST_MANAGER_WALLET)
        Configuration.set("NETWORK_TRUST_MANAGER_PUBLIC", NETWORK_TRUST_MANAGER_PUBLIC)
        Configuration.set("NETWORK_TRUST_MANAGER_PID", NETWORK_TRUST_MANAGER_PID)
        Configuration.set("ASQI_WALLET", ASQI_WALLET)
        Configuration.set("ASQI_WALLET_PUBLIC", ASQI_WALLET_PUBLIC)
        Configuration.set("FOUNDATION_WALLET", FOUNDATION_WALLET)
        Configuration.set("FOUNDATION_WALLET_PUBLIC", FOUNDATION_WALLET_PUBLIC)
        Configuration.set("SENTINEL_NODE_WALLET", SENTINEL_NODE_WALLET)
        Configuration.set("SENTINEL_NODE_WALLET_PUBLIC", SENTINEL_NODE_WALLET_PUBLIC)
        Configuration.set("DAO_MANAGER", DAO_MANAGER)
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        Configuration.updateDataFromDB(cur)
        return True

    @staticmethod
    def updateDataFromDB(cur):

        data = cur.execute(f'''select property_key,property_value from configuration''')
        data = data.fetchall()
        for i in data:
            Configuration.set(i[0], i[1])
        return True


