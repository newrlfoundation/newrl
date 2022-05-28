"""Python programm to create the genesis block with a given chain creator wallet address"""
import json
import os
import shutil

from .blockchain import Blockchain
from ..constants import MEMPOOL_PATH


def main():
    blockchain = Blockchain()
    print("Loaded chain validity status : ",
          blockchain.chain_valid(blockchain.chain))

    empty = []
    with open("empty.json", "w") as writefile:
        json.dump(empty, writefile)

    if not os.path.exists("all_wallets.json"):
        #	shutil.copy("creatorwalletdata.json","all_wallets.json")
        print("all_wallets.json does not exist, creating. Signing won't work till valid addresses added to it.")
        allw = []
        with open("all_wallets.json", "w") as writefile:
            json.dump(allw, writefile)
    else:
        print("all_wallets.json already exists. Signing will work for addresses in it.")

    if not os.path.exists("all_tokens.json"):
        shutil.copy("empty.json", "all_tokens.json")
    else:
        print("all_tokens.json already exists.")

    print("Making mempool, incltranspool and statearchive directories")
    if not os.path.exists(MEMPOOL_PATH):
        os.mkdir(MEMPOOL_PATH)
    else:
        print("WRN: Mempool already exists, beware of possible errors")


if __name__ == "__main__":
    main()
