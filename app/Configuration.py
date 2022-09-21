import json
import sqlite3

from app.codes.clock.global_time import get_corrected_time_ms
from app.constants import NEWRL_DB
from app.nvalues import *


class Configuration:
    conf = {
        "ZERO_ADDRESS": ZERO_ADDRESS,
        "TREASURY_WALLET_ADDRESS": TREASURY_WALLET_ADDRESS,
        "NETWORK_TRUST_MANAGER_WALLET": NETWORK_TRUST_MANAGER_WALLET,
        "NETWORK_TRUST_MANAGER_PUBLIC": NETWORK_TRUST_MANAGER_PUBLIC,
        "NETWORK_TRUST_MANAGER_PID": NETWORK_TRUST_MANAGER_PID,
        "ASQI_WALLET": ASQI_WALLET,
        "ASQI_WALLET_DAO": ASQI_WALLET_DAO,
        "ASQI_WALLET_PUBLIC": ASQI_WALLET_PUBLIC,
        "FOUNDATION_WALLET": FOUNDATION_WALLET,
        "FOUNDATION_WALLET_DAO": FOUNDATION_WALLET_DAO,
        "FOUNDATION_WALLET_PUBLIC": FOUNDATION_WALLET_PUBLIC,
        "SENTINEL_NODE_WALLET": SENTINEL_NODE_WALLET,
        "SENTINEL_NODE_WALLET_PUBLIC": SENTINEL_NODE_WALLET_PUBLIC,
        "DAO_MANAGER": DAO_MANAGER,
        "CONFIG_DAO_ADDRESS": CONFIG_DAO_ADDRESS,
        "STAKE_CT_ADDRESS": STAKE_CT_ADDRESS,
        "STAKE_PENALTY_RATIO": STAKE_PENALTY_RATIO,
        "MIN_STAKE_AMOUNT": MIN_STAKE_AMOUNT,
        "STAKE_COOLDOWN_MS": STAKE_COOLDOWN_MS,
        "FOUNDATION_DAO_ADDRESS": FOUNDATION_DAO_ADDRESS,
        "ASQI_DAO_ADDRESS": ASQI_DAO_ADDRESS,
        "NETWORK_TREASURY_ADDRESS": NETWORK_TREASURY_ADDRESS,
        "MEMBER_WALLET_LIST" : json.dumps(MEMBER_WALLET_LIST),
        "FOUNDATION_TREASURY_ADDRESS" : FOUNDATION_TREASURY_ADDRESS,
        "ASQI_TREASURY_ADDRESS" : ASQI_TREASURY_ADDRESS
        }
    setters = ["ZERO_ADDRESS",
               "TREASURY_WALLET_ADDRESS",
               "NETWORK_TRUST_MANAGER_WALLET",
               "NETWORK_TRUST_MANAGER_PUBLIC",
               "NETWORK_TRUST_MANAGER_PID",
               "ASQI_WALLET",
               "ASQI_WALLET_PUBLIC",
               "FOUNDATION_WALLET",
               "FOUNDATION_WALLET_PUBLIC",
               "SENTINEL_NODE_WALLET",
               "SENTINEL_NODE_WALLET_PUBLIC",
               "DAO_MANAGER",
               "ASQI_PID",
               "NETWORK_TREASURY_ADDRESS",
               "ASQI_DAO_ADDRESS",
               "FOUNDATION_DAO_ADDRESS",
               "CONFIG_DAO_ADDRESS",
               "STAKE_COOLDOWN_MS",
               "MIN_STAKE_AMOUNT",
               "STAKE_PENALTY_RATIO",
               "STAKE_CT_ADDRESS",
               "MEMBER_WALLET_LIST",
               "ASQI_TREASURY_ADDRESS",
               "FOUNDATION_TREASURY_ADDRESS"

               ]

    @staticmethod
    def config(name):
        return Configuration.conf[name]

    @staticmethod
    def set(name, value):
        Configuration.conf[name] = value

    @staticmethod
    def init_values():
        Configuration.set("ZERO_ADDRESS", ZERO_ADDRESS)
        Configuration.set("TREASURY_WALLET_ADDRESS", TREASURY_WALLET_ADDRESS)
        Configuration.set("NETWORK_TRUST_MANAGER_WALLET", NETWORK_TRUST_MANAGER_WALLET)
        Configuration.set("NETWORK_TRUST_MANAGER_PUBLIC", NETWORK_TRUST_MANAGER_PUBLIC)
        Configuration.set("NETWORK_TRUST_MANAGER_PID", NETWORK_TRUST_MANAGER_PID)
        Configuration.set("ASQI_WALLET", ASQI_WALLET)
        Configuration.set("ASQI_WALLET_DAO", ASQI_WALLET_DAO)
        Configuration.set("ASQI_WALLET_PUBLIC", ASQI_WALLET_PUBLIC)
        Configuration.set("FOUNDATION_WALLET", FOUNDATION_WALLET)
        Configuration.set("FOUNDATION_WALLET_DAO", FOUNDATION_WALLET_DAO)
        Configuration.set("FOUNDATION_WALLET_PUBLIC", FOUNDATION_WALLET_PUBLIC)
        Configuration.set("SENTINEL_NODE_WALLET", SENTINEL_NODE_WALLET)
        Configuration.set("SENTINEL_NODE_WALLET_PUBLIC", SENTINEL_NODE_WALLET_PUBLIC)
        Configuration.set("DAO_MANAGER", DAO_MANAGER)
        Configuration.set("CONFIG_DAO_ADDRESS", CONFIG_DAO_ADDRESS)
        Configuration.set("STAKE_CT_ADDRESS", STAKE_CT_ADDRESS)
        Configuration.set("STAKE_PENALTY_RATIO", STAKE_PENALTY_RATIO)
        Configuration.set("MIN_STAKE_AMOUNT", MIN_STAKE_AMOUNT)
        Configuration.set("STAKE_COOLDOWN_MS", STAKE_COOLDOWN_MS)
        Configuration.set("FOUNDATION_DAO_ADDRESS", FOUNDATION_DAO_ADDRESS)
        Configuration.set("ASQI_DAO_ADDRESS", ASQI_DAO_ADDRESS)
        Configuration.set("NETWORK_TREASURY_ADDRESS", NETWORK_TREASURY_ADDRESS)
        Configuration.set("ASQI_PID", ASQI_PID),
        Configuration.set("MEMBER_WALLET_LIST", json.dumps(MEMBER_WALLET_LIST))
        Configuration.set("FOUNDATION_TREASURY_ADDRESS",FOUNDATION_TREASURY_ADDRESS)
        Configuration.set("ASQI_TREASURY_ADDRESS",ASQI_TREASURY_ADDRESS)
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        Configuration.updateDataFromDB(cur)
        return True

    @staticmethod
    def init_values_in_db():
        con = sqlite3.connect(NEWRL_DB)
        cur = con.cursor()
        count = cur.execute(f'''select count (*) from configuration''').fetchone()
        if count is None or count[0] == 0:
            for i in Configuration.setters:
                value = Configuration.config(i)
                queryParam = {"address": CONFIG_DAO_ADDRESS,
                              "property_key": i,
                              "property_value": value,
                              "is_editable": True,
                              "last_updated": get_corrected_time_ms()
                              }
                keys = ','.join(queryParam.keys())
                question_marks = ','.join(list('?' * len(queryParam)))
                values = tuple(queryParam.values())
                cur.execute('INSERT OR IGNORE INTO  configuration (' + keys + ') VALUES (' + question_marks + ')',
                            values)
        cur.close()
        con.commit()
        con.close()

    @staticmethod
    def updateDataFromDB(cur):

        data = cur.execute(f'''select property_key,property_value from configuration''')
        data = data.fetchall()
        for i in data:
            Configuration.set(i[0], i[1])
        return True


