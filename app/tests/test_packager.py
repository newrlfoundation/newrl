import json
import requests
from app.codes.p2p.packager import compress_block_payload, decompress_block_payload


def test_pack_unpack_block():
    original_block = {
        "index":
        8394,
        "hash":
        "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
        "data": {
            "index":
            8394,
            "timestamp":
            1661510690000,
            "proof":
            0,
            "text": {
                "transactions": [{
                    "transaction": {
                        "timestamp": 1661510640000,
                        "trans_code":
                        "5296d933b19dd83e135148d550b63d4cb34dc340",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xa930b3bfa82219198ad3b0c895acf1211e669053",
                            "network_address": "3.83.91.42",
                            "broadcast_timestamp": 1661510640000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xa930b3bfa82219198ad3b0c895acf1211e669053",
                        "msgsign":
                        "D0VCtqDodcIzSLnqoPBoAMGMnHZsFiGnGCu1bYPNdsrd+OiUihU1gfGic/5h3cd6E+xy7wOFSGYY9Gc92dcf/w=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510641000,
                        "trans_code":
                        "8ebf17bf951fd4b836ae517c9286c10e1b61102b",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x2454432d453bdc5d5bddfe1ee04808bfeffbdb92",
                            "network_address": "3.83.146.254",
                            "broadcast_timestamp": 1661510641000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x2454432d453bdc5d5bddfe1ee04808bfeffbdb92",
                        "msgsign":
                        "rlweuV5UWZ94uKcODjhuc+OZWfYNPVwggI9K4unRnGc+yv4yXTxw2PdR0/tmFluBMCgjn81OiEWvTMCBc+GxRQ=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510654000,
                        "trans_code":
                        "c39f0a40db4906980bb2c8ed61895c2cc38fd1d3",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xc4598a89c1dd184afdcffc8257c927848c774c59",
                            "network_address": "3.83.212.229",
                            "broadcast_timestamp": 1661510654000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xc4598a89c1dd184afdcffc8257c927848c774c59",
                        "msgsign":
                        "1t0kxEMkL/3eim0NPHSQd2ljuS1PXsD2KanNGOXRyCZAar15QegB6gNeazRIpjDC8wZlUwmxzfe+RMVkWTZ1+w=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510656000,
                        "trans_code":
                        "44c3628c3031e3f0f7ce9f8a59a432f524af6761",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x29d19ecbffae9ad314805aaf52b3ae95b8b3c8bf",
                            "network_address": "52.207.183.115",
                            "broadcast_timestamp": 1661510656000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x29d19ecbffae9ad314805aaf52b3ae95b8b3c8bf",
                        "msgsign":
                        "lc7cglAlFw53+2iZ/n8laRCwCeM3VxEZGCPa8tGS1OToBORN+SdcxSYQmKhDieXZgzLADyGiuc/n2tIegYosDA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510660000,
                        "trans_code":
                        "e7caa3712c72f366e435d06783f0648dbe81934b",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x37bf5b0973c22e4f89bc3afb1fcf5498b66402c9",
                            "network_address": "54.224.250.52",
                            "broadcast_timestamp": 1661510660000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x37bf5b0973c22e4f89bc3afb1fcf5498b66402c9",
                        "msgsign":
                        "ochUmk7Y5wOpQMRtvOqi6/MHzfZr6cKfKJGqO0jU7XOuDCE1jdHAA/uus+qpIXOgzhQFL/drKBRkuNSTwmFi1Q=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510664000,
                        "trans_code":
                        "d0771c5caa0d1e227e0cf8132a407a124f4d39e5",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x0ef4c18344c80f7e08cbad80296347efabf541b5",
                            "network_address": "18.207.196.241",
                            "broadcast_timestamp": 1661510664000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x0ef4c18344c80f7e08cbad80296347efabf541b5",
                        "msgsign":
                        "gDKa4WhISeLOrpP1PD1t6mkTUpPcgIWApWHg2dD2UgZQqfwhLmTqi7RjcwOHiB+kQJAR8djQ4WZNysTzAygsMA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510666000,
                        "trans_code":
                        "35d677eba903b090207e2ef093ce8d728c8eb4de",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xda50a98b9f954f54ec74c72befa84bc6d4ca2c80",
                            "network_address": "3.86.167.138",
                            "broadcast_timestamp": 1661510666000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xda50a98b9f954f54ec74c72befa84bc6d4ca2c80",
                        "msgsign":
                        "N1UZYliFx/KLZAA+t/kkipm47ecFJAHZysMGC9UOlz6CbmeaI2OdeoHmDAwJ73oScCFbvLX6UFVnqJtPhzMqXA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510671000,
                        "trans_code":
                        "56da6a32878eff79b97bd57aa0b8abf44a67faab",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xf9c176dda928456595f4058dd17c0b163bdb757c",
                            "network_address": "3.85.165.194",
                            "broadcast_timestamp": 1661510671000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xf9c176dda928456595f4058dd17c0b163bdb757c",
                        "msgsign":
                        "aR6tfKPBqty23AWaat0w3CeEdjE5amZlGLs3/7rEUEyKp3z7dx+n0n51/yuYM1jtQi/bznEeKWgU3LiLPS/r5g=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510675000,
                        "trans_code":
                        "73c627afa184c2aa4a4e720b7c76c2555ffe7620",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xa8ff225f805064b23d66cee6442a2af328f18f06",
                            "network_address": "3.82.158.205",
                            "broadcast_timestamp": 1661510675000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xa8ff225f805064b23d66cee6442a2af328f18f06",
                        "msgsign":
                        "lpL+jP8blXTyQqa3n9nPfLn8FOwsx6uN86XnIiEE4Cpm0RSBywe6x3pWmDlb4Mnn8CvNl0aBtwf7VP9E7yTKAw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510679000,
                        "trans_code":
                        "e3ffded53de4c1eb1256f648ee3301f091d18fd1",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x5e9090aa227fdc8c6e1fbce19c2a9a2dc508ac7d",
                            "network_address": "44.204.80.162",
                            "broadcast_timestamp": 1661510679000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x5e9090aa227fdc8c6e1fbce19c2a9a2dc508ac7d",
                        "msgsign":
                        "PVI/YSii4m2R4hdxCCTrQqXLtmHaflYWOLP3JCzV3/nb+Ir0w1TYe9ESCL9gTslX9f2ooWsvtktQfSdSyfsvvg=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510683000,
                        "trans_code":
                        "056c4b908c847a098d0da38959a19d5137a6c32b",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x26be122c543fa729b3b04492c7a99d1b8e44a751",
                            "network_address": "3.85.228.253",
                            "broadcast_timestamp": 1661510683000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x26be122c543fa729b3b04492c7a99d1b8e44a751",
                        "msgsign":
                        "L+zwvzXU5Uv9Cx1NU9lN+gzge80oln8MFSMv8MpeOntb8gUweK55JBj6SxAggse2Bv6wtU2KuwrFLCZjX8HNOw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510689000,
                        "trans_code":
                        "89c4fe3de19911eb68673d68b2d3cd655b96c2b5",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x36e8ed26a22d928b709c73b607181198e97c0e83",
                            "network_address": "3.82.196.109",
                            "broadcast_timestamp": 1661510689000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x36e8ed26a22d928b709c73b607181198e97c0e83",
                        "msgsign":
                        "0Zw+rmGW7RIKPLd4q9rOMYZTTMFarRcLK2OWUoVbd5S1IeoMOxRR7+m3+SExMzQcRtYFJVNa8whJscMPuLgqnA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510657000,
                        "trans_code":
                        "2b28ef9e1876f07ce18f1ace183a74196a03474b",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x58a7bb34ca0d8a627dee1fb9117d8320ae2f5602",
                            "network_address": "3.85.160.133",
                            "broadcast_timestamp": 1661510657000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x58a7bb34ca0d8a627dee1fb9117d8320ae2f5602",
                        "msgsign":
                        "IEq5s2XoHA+riXv8Z12Aw+MHZkpaqccFx1cslSQrZl+xka4lpsZA1kam4n7Teco6duxlDZkL+a7z4VLRC6I0Qw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510661000,
                        "trans_code":
                        "c50763db640d56fa815f66562cf17c8b9f9ff817",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xbe4748f74536e5c3401d43f6eb04d4d9546e272c",
                            "network_address": "3.82.218.74",
                            "broadcast_timestamp": 1661510661000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xbe4748f74536e5c3401d43f6eb04d4d9546e272c",
                        "msgsign":
                        "OGdPDAU04vU2PxwjIy/2JXzjV/f838YINDNA/89m3MESiHOSjE74o1/6k9O72O/kOmAyZVEiPtYV/xZj8aY09Q=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510664000,
                        "trans_code":
                        "d800fed69af0e4736f3c4a87c561e62561976e08",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x63cdf38113dabc61dbaa60846b6b1e396ba8d2db",
                            "network_address": "54.89.105.194",
                            "broadcast_timestamp": 1661510664000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x63cdf38113dabc61dbaa60846b6b1e396ba8d2db",
                        "msgsign":
                        "TlAv3Gsy/j/9t3UnGiOp37DDMuhyi3XGf2duI+PCfrkytu4yhvdn9sQpfdA3xlJy1PF/Lw1BaFfjqdRsuHqZDw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510669000,
                        "trans_code":
                        "24b0f5f1e232341dd5c958c5f97733d586225c53",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x2382aa488e3a6b5a275424558f9093689701e714",
                            "network_address": "54.159.200.227",
                            "broadcast_timestamp": 1661510669000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x2382aa488e3a6b5a275424558f9093689701e714",
                        "msgsign":
                        "fVAZtDxot4DwNGBBUa8fgpFPJSeYV6dvZDjs7s4/B9KjsB4/AoEUhwldKId/dToddluz0m+SyBHLixmQ2dTh7g=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510672000,
                        "trans_code":
                        "be7149a045eeb4715edf22949ce129c94e74a637",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x79274216a3a7f5e26751d8d53315c3ddf94a2425",
                            "network_address": "18.212.200.85",
                            "broadcast_timestamp": 1661510672000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x79274216a3a7f5e26751d8d53315c3ddf94a2425",
                        "msgsign":
                        "3ptiyEO3NThsa1GW7N8MQ9QC1WQEsdVFm4Y2ZtwORqonfJ8jnAzZ8+/+nI1Y1sQBlk7KLWBtuWFYfoq9h50F7g=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510676000,
                        "trans_code":
                        "d7a28f05bf48a785fcc0e80e64ceb61772a1d31d",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x6b5a0138e440cc2edd78a3763de0bf15c33ac5a9",
                            "network_address": "3.94.10.30",
                            "broadcast_timestamp": 1661510676000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x6b5a0138e440cc2edd78a3763de0bf15c33ac5a9",
                        "msgsign":
                        "tU4BHgiTgg+XY5nRz9DgogifuYHI8SNz90pPngPRcYWPWOPOY4Ag2R9rZGpmV17Nw9yTb8qvKHtIScvIWp/YdA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510681000,
                        "trans_code":
                        "f24cd4bc12fe7e71408997d787ad8bb8e2f32be7",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x08f16acc9c6204e9004cc754886a03dc01a4fe9e",
                            "network_address": "18.204.197.253",
                            "broadcast_timestamp": 1661510681000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x08f16acc9c6204e9004cc754886a03dc01a4fe9e",
                        "msgsign":
                        "e/T19uh8OrH5wzzgydy67szdMnO3QLKDLDjpilpo7CFdsljyF5w5dkZpL5a6qoiv2IKE4vq9C4NpQExO4AiCuA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510684000,
                        "trans_code":
                        "854158f29eaeb94391c17c91d5b09aa3334770ec",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xca812e57cd0a053e9f82065992362f5a24e522c8",
                            "network_address": "52.90.220.119",
                            "broadcast_timestamp": 1661510684000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xca812e57cd0a053e9f82065992362f5a24e522c8",
                        "msgsign":
                        "HDqoWyIRdxEcmnraeUjvrcsbdoY/gdRJPz7ptnQAtMGWgdRSHgVZhza3zVtF/eVD1vb+Vl5jkxQiecReYDUiMQ=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510689000,
                        "trans_code":
                        "f319ad4d90d66e064084a68d13ea0fb60bde1490",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x5c7757adcf8e5c5b1d50b312a75bc52862418bce",
                            "network_address": "54.146.176.153",
                            "broadcast_timestamp": 1661510689000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x5c7757adcf8e5c5b1d50b312a75bc52862418bce",
                        "msgsign":
                        "FpocGYLo9V9+6kYoThmdSFb77rGVwxmyji5B35yeROlg/rBqHUO1Rm703Jl1GCTuXckpGWBU9DAd/f5PQH+NzQ=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510689000,
                        "trans_code":
                        "79fee22ea022724dc4f9b8be1b3b34a8c2bd6886",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xe8d2125d53716b98317d86697c2ba4bb7e5ffda3",
                            "network_address": "3.83.224.97",
                            "broadcast_timestamp": 1661510689000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xe8d2125d53716b98317d86697c2ba4bb7e5ffda3",
                        "msgsign":
                        "jyIp59w7TD53fOF6SXOOmXOrmun5FTeD3EOnwSVm6kmjfYXA+2Y13I6UFZcK0mCu3nih1/Ru7y+SKiPLQH9uHA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510689000,
                        "trans_code":
                        "42888005bad05026e649a7517cd1f800089eba09",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x4af1becce964cc86b86f78542c407f343cbebcbc",
                            "network_address": "54.173.203.193",
                            "broadcast_timestamp": 1661510689000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x4af1becce964cc86b86f78542c407f343cbebcbc",
                        "msgsign":
                        "RFFQlM2cQdvpwqeEwEUC/APhPjur6JQy80RuyqnkkvXX/6MEfPi1JMnu0dd4jd/J5VcXxumnN4orLoemZTFmhw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510642000,
                        "trans_code":
                        "dc5a25c121389c4c3bba552fb8ad3a19f9c1134a",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x479745b81f6011cb966873a574a32ef2bf7c2092",
                            "network_address": "44.203.5.255",
                            "broadcast_timestamp": 1661510642000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x479745b81f6011cb966873a574a32ef2bf7c2092",
                        "msgsign":
                        "zvq3xNvBfgoaPSXEQhlZg+1miVUpg4nFBki/6COaK8ApG/nR02+IfnptAjKXBoBJtIMASmtMm+qZODwnhKEohA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510646000,
                        "trans_code":
                        "b322b0ef8d4d1543ee2afcaa7408fc7fab57ddcd",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x57007e69cb1459b97b667272841ced4289c109dd",
                            "network_address": "44.203.161.237",
                            "broadcast_timestamp": 1661510646000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x57007e69cb1459b97b667272841ced4289c109dd",
                        "msgsign":
                        "T8RHDAYMct0MOZF6aLgl0jSu0dKUGazErX5Th2Lpq4QVc7/a2mUTLCixwhiB9ubQjfd8Af1+zBa7ezXKahhitA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510647000,
                        "trans_code":
                        "202e175672622605fa1c974916865c6753dd0e6e",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x9fd9ffeff71a0bbbcdf9761445e156a447c9ac14",
                            "network_address": "54.210.161.198",
                            "broadcast_timestamp": 1661510647000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x9fd9ffeff71a0bbbcdf9761445e156a447c9ac14",
                        "msgsign":
                        "Updep1MIh2IiG2K/JcLua5gtkwTmQeF8YXy4H9byjKpLEg/DtL1Pbq9SgoMAbpjx1nNSc1qqJ/epfGPHsvzh6Q=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510648000,
                        "trans_code":
                        "4902b22a368e269d2487b88dba54161e2c48caa8",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xeab19a76888872002291d46ccdad7078e9349dcb",
                            "network_address": "44.202.237.105",
                            "broadcast_timestamp": 1661510648000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xeab19a76888872002291d46ccdad7078e9349dcb",
                        "msgsign":
                        "OFsol2B8qAc/SY5b4nnY+Q4CLnC43NdiNy9S4L5io43sH7vhPKtMKmM/bxIUHwV51rYQcu78hy5IE6iylZHa5w=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510649000,
                        "trans_code":
                        "16b70e92eb734f5c2fd29dceb605c15348abf4a7",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xf98ec14bd533c201933df4f6c3fbe03da5fc4027",
                            "network_address": "34.239.102.237",
                            "broadcast_timestamp": 1661510649000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xf98ec14bd533c201933df4f6c3fbe03da5fc4027",
                        "msgsign":
                        "ELy8xW3LFbWovUvSkzusrCwT0uN0S93nATUHsnbnz1oYbHXFoit6mZJzwKNEjhesnmgWfkOPsBu4e5FVQFmJQw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510650000,
                        "trans_code":
                        "b85e6297e4e4f323575ae252c9c15806489db832",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xb719cbb2340a5ba11f7bf6a0c8be3a4724c8b614",
                            "network_address": "18.208.170.83",
                            "broadcast_timestamp": 1661510650000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xb719cbb2340a5ba11f7bf6a0c8be3a4724c8b614",
                        "msgsign":
                        "U+LXBBf/uWs+nw7Ux5v41zBxbaxw+vc6O4+HjPWxOAojnh9fU/ptcofpJyp7l1CK+XfETIn69vyVsKvTB3qsxA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510651000,
                        "trans_code":
                        "18478db1667a739063b9da0abef834b9143f2574",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x45ad5076e13eb57692728224fbb15719b20f9777",
                            "network_address": "3.83.50.49",
                            "broadcast_timestamp": 1661510651000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x45ad5076e13eb57692728224fbb15719b20f9777",
                        "msgsign":
                        "2I3ZkH/ls4n31S+FMHYUBmyXpWw5XdyvLpApiNnuuiBUPTxJYa4c/70DlFVwKRa+0rFf4uW4gtAoC29h+ML8CA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510652000,
                        "trans_code":
                        "8ba95516b205fe45ce67eaa2437886a926a73c1c",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xb481b480a1c46d1a28812aa2be5012292d88b48b",
                            "network_address": "3.94.187.156",
                            "broadcast_timestamp": 1661510652000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xb481b480a1c46d1a28812aa2be5012292d88b48b",
                        "msgsign":
                        "h5VqaCsGviGLbi6Eijt6KUbcL1P2OqMSd05BUpdpLkeWupmEa08ihdmz3xqSdYd1qO6Ogadkd02JDSOXvZWf/A=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510653000,
                        "trans_code":
                        "43e9893d88bbbaaf8f570a89d375f5474b203b54",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x70a1bc5faa2c6d996ece06a5519ecdfa0a1ad77c",
                            "network_address": "3.86.98.169",
                            "broadcast_timestamp": 1661510653000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x70a1bc5faa2c6d996ece06a5519ecdfa0a1ad77c",
                        "msgsign":
                        "LlkSP/8lrtshw2PQHZw8+cbTW+drXeB7/298T1Yd3G1qhwemJtOSKPO8fj0RfcreAVfUu+2ZMTVHMhIIPRFC3g=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510655000,
                        "trans_code":
                        "0844e40533ccda8f434fcdce012fc709ca1ebd8c",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x02bdef8fab83d70381ba8b9c7046111cf5e14b44",
                            "network_address": "3.84.220.188",
                            "broadcast_timestamp": 1661510655000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x02bdef8fab83d70381ba8b9c7046111cf5e14b44",
                        "msgsign":
                        "krrr4eanggGUyMEJjmb94MuJqNC4Gl0aw8pViAfdNcV9G7y/ieY9FF4dAcVzdochCrn5XfDmL5HwuNGD0abfXw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510659000,
                        "trans_code":
                        "e6db8614b168e5c065007727fdabe723067549ee",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xb795950b437d3012109da3787de6c7026815edfa",
                            "network_address": "44.206.234.8",
                            "broadcast_timestamp": 1661510659000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xb795950b437d3012109da3787de6c7026815edfa",
                        "msgsign":
                        "ZC9Kauvp0o4DQJnWRR1hyhug29HjtNcGn4jmPhC3K3ecDDajNxnvmaw8dnNLDuMn0cLFWCVP5MJhh32+c8Op4Q=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510662000,
                        "trans_code":
                        "7b56096bc5c3cbb5e1b4c7d218c6b4e36dae7de4",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xe9db349e9e105d5d4d8d2b45e77791bd0e935b01",
                            "network_address": "3.86.207.126",
                            "broadcast_timestamp": 1661510662000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xe9db349e9e105d5d4d8d2b45e77791bd0e935b01",
                        "msgsign":
                        "xV2CeW7OsuXlITqAZzxymuL4Dxi4KgMbQwJny0YhovOJ6PBoNW2A1PwoDKqO0WlpMlmchef78uNJa3yv4uUtuw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510666000,
                        "trans_code":
                        "c1b6157886c325164f5f48de8f6ce67294552290",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x5dafceb4c248c8d745cb3ee086ac226fce8585dc",
                            "network_address": "3.87.42.189",
                            "broadcast_timestamp": 1661510666000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x5dafceb4c248c8d745cb3ee086ac226fce8585dc",
                        "msgsign":
                        "LNfaA2RjJIMobr747KzNr4iPwzKfeBVkgPYyyJ5t0ziYJXoDp8aqqirBgNmKP+JTDw10FseWyreAeNLvePD0QQ=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510670000,
                        "trans_code":
                        "cfca8e974e84dcaed278c98f16ce1b10d3564b23",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0x878d6f1f349b371510437ab5fdb58525b4c969fd",
                            "network_address": "44.202.129.30",
                            "broadcast_timestamp": 1661510670000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0x878d6f1f349b371510437ab5fdb58525b4c969fd",
                        "msgsign":
                        "WFWaTN5ClEfkFM+UeRgI/bScxUWz/jYaa3BqgL+o0Izw/ns2hv82W/f/NovkIaqdUw8kWK3+TxFQa1LpSjB1aw=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510682000,
                        "trans_code":
                        "749426bb5537edba03acfad853737587207c240a",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xec835b955e426e940f7e70cf7fb29138068e1cb6",
                            "network_address": "100.26.188.16",
                            "broadcast_timestamp": 1661510682000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xec835b955e426e940f7e70cf7fb29138068e1cb6",
                        "msgsign":
                        "es3VXcR8n7YKRrK6pE/2TPqV+esh42yJO16Wzto65mStnuFsZXQkz1hMYEBC4gSnlRIDWQS6JLyvX0TMQ4T43Q=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510687000,
                        "trans_code":
                        "3fe50d243eb85c380a49ff7daea3a177902d69d0",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xbd5e3ff29cb458a91c5a182bc511d879c8c39cb6",
                            "network_address": "44.204.23.78",
                            "broadcast_timestamp": 1661510687000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xbd5e3ff29cb458a91c5a182bc511d879c8c39cb6",
                        "msgsign":
                        "h7mqO1nRRBir7ogwdd4J0TXB+aLEm6nXhakr4ndtMlg2RsaRASPlPcBLi+hPzu82yEg0zwszau6e9qRU3PenoA=="
                    }]
                }, {
                    "transaction": {
                        "timestamp": 1661510690000,
                        "trans_code":
                        "a888bd215ca949abc3b22868ccd0deb80bbd0cad",
                        "type": 7,
                        "currency": "NWRL",
                        "fee": 0.0,
                        "descr": "Miner addition",
                        "valid": 1,
                        "specific_data": {
                            "wallet_address":
                            "0xb4b54cf868d142dc38b3087dc89f7ac422e2bf60",
                            "network_address": "18.212.52.66",
                            "broadcast_timestamp": 1661510690000,
                            "software_version": "1.1.1",
                            "last_block_index": 8393
                        }
                    },
                    "signatures": [{
                        "wallet_address":
                        "0xb4b54cf868d142dc38b3087dc89f7ac422e2bf60",
                        "msgsign":
                        "ptwrZPY/RV45SnXgXYmLEBS0KvVREdukjzI+62eqdpla/Jz5HNL9GscW9L5HmBcjBUsLamFXRRNg+k7lxloZgw=="
                    }]
                }],
                "previous_block_receipts": [{
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        9,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0x97694d38c5c8ca9c219bdaa3411c7955bbef7568"
                    },
                    "public_key":
                    "F+gY0DPPdnlTt1YpHrduZPmsa4mYGV2a10JzumlO4eXAidUqqatw7OiZPAJnvlGKXKpd0Jf2pho3dS7cYKk/ug==",
                    "signature":
                    "53p9Jmb3+vo0qD9eA/GhQUnOWbi45HNGd+FkCyXkm+BDbh0BsK29tRZBTOP2Id7/rypIpP4RglzT2sDEselWww=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0x4ab4d18e34cb98cb547d198f729b16535a331c29"
                    },
                    "public_key":
                    "z6fzRh7Irdlr21k7pjRlt05rljTcnMIx1nfQB559Gg5Ta9o5P4qaxOmrfdAiNbbOz1lRSoQag+xqH8701JT8mw==",
                    "signature":
                    "tJmqzJajrRorIycrAs5ozpQP7rTfOfG4V4wTxQFLSygQVPM5Zbsk9jTAzdxjH8OBuixsMJ+sSKhUE5SChEvm/g=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0x76a806133d94413ede530550cdd77914b1f8f8fc"
                    },
                    "public_key":
                    "z/3nbUpw8AH/n4mRF9KAB6/RwJZOE4By0jLDkkUCTS/ud5yx0SHSSliriWIakvUYFBy0Gss8xHDqlK7bWonAmw==",
                    "signature":
                    "WHJad0fXcnU6ykxbkrjVBRkZAJN894i2sbNNG0vSnBSoPjOgMEDmh4hVaeiExpLds+CE/Ozz4/QitCcj7Ohhng=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0x2bbd1c0d18198c386893ff8409ab5e01da29672d"
                    },
                    "public_key":
                    "5srIPNG2Hg/YrsPEQF3y0d+YTJubU8egIeRFnJ92zKO5DHQ2SqYTYAOPcZ0/lwqMOZb+mahH3KTwHV/tEGK9/w==",
                    "signature":
                    "83xvKJSbYGuu6AKr/v6tnJCzRRXpfL3GBEAF+fttCNjEiEXZVqvszoKgYwJvZ85ggxt2CBu6gsErn5xyJildow=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0x345627a397957558d2986dcdc3784c140cc387eb"
                    },
                    "public_key":
                    "z0S6hCItA+U2VXC+p4YtAEM02FMyaWEhJBz39B00WTIfOJmuCaQI6K4p5NR2RpB3LJqG62ys01eqa54nfXSYxg==",
                    "signature":
                    "EVbawDncb2dYVkMazPhEbl9Y92UEFpIRGJ9epVoUvVnW1sQzOktGrgX7dpXpeodzDAVohJYgJ9QHmNKnxqUIVQ=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0xf2303cb168f2b096d9f75cb65c5a039b1b1a0e87"
                    },
                    "public_key":
                    "hJn0zdokRbcaLhNz8MVWu8C8gvor4E0lq2lgyuIfZgxH4sh3LzlaonpgH7nQARNwq6Y8HUxSL5gofLQD0OC5bw==",
                    "signature":
                    "KjZ6oD2zLmskV6r2JuG5rXiXZLc5IXovArpYgF10JsdP2Pu9QAbMzjW6/KgZKoKX+QBU6HA7uegIwz6/TqOyfw=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0xbd5e3ff29cb458a91c5a182bc511d879c8c39cb6"
                    },
                    "public_key":
                    "4UaD0L1qIeGwDdYcNupgUFqyxLmqNiddYfHQ07WStnBjUi5a3Np0/Gdjjz5vU7HKzHql6TdtvgM5NvAt1oUUEw==",
                    "signature":
                    "J711XUh/sAYyVYRdTKFwJYvA/K+Ca/XSRJ56UQ1OkmVIxPzBqLIctKgRIY3K0gI8cDfNmlXkriF/tX0OyJHuzA=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0xd025b9ab7996d3c7bc0c499337711b63f8d306ea"
                    },
                    "public_key":
                    "RRbxr4AFjewkVIwddEgzQMkjKA+nGhGWSXqTbK1HNguuAZ+RPjzy3fzdqW7Zw0+w9hLWMvLDiD7KUPxkbib77Q==",
                    "signature":
                    "GXirMF+mW1GEOclCIVpjWQhfN9NvtmvCjEmE2aSgnIXnW18EAhyUOpljeuBM/pqzYQUC1vx5H8zVNvZlAhCnhg=="
                }, {
                    "data": {
                        "block_index":
                        8378,
                        "block_hash":
                        "688e173112ee890e923e6124789616720c12a556eda8eb6f114e17287a0a968d",
                        "vote":
                        1,
                        "timestamp":
                        1661510144000,
                        "wallet_address":
                        "0x479745b81f6011cb966873a574a32ef2bf7c2092"
                    },
                    "public_key":
                    "xeWR5fOtn8hFwLgwh/b06iJ7HAj7N1vLLlKlg9Qt3uZtFXN3XWeR9o7zkM4CzRnoS5ykQxVahmy3PRVtJS/mzw==",
                    "signature":
                    "c3KHS2cIePe1/Hj+d94r3FOeFb10a7VFqj4dPCdSA9UJdNELK4XUKV8wxb7BL3m/phsoucT/8WCkeF43d4EVxA=="
                }]
            },
            "creator_wallet":
            "0x70a1bc5faa2c6d996ece06a5519ecdfa0a1ad77c",
            "expected_miner":
            "0x70a1bc5faa2c6d996ece06a5519ecdfa0a1ad77c",
            "committee": [
                "0x293c137a8b647b59dba28265e24e9e9040daa86c",
                "0x430c49495097021d346b3d38abb44b990e17da38",
                "0x45ad5076e13eb57692728224fbb15719b20f9777",
                "0x70a1bc5faa2c6d996ece06a5519ecdfa0a1ad77c",
                "0x8aa253c22c19f8559d6de0df1cfbc053b5cb76ae",
                "0xa0345e65f0702be8b87845db9390e820df154d4a",
                "0xc3c02fb139c2f518924f9a7f3b37cb303c8aac84",
                "0xdcb66aff33c4e0f7f4f7e02f9fb7d378106a6c9d",
                "0xf1f4e36072f485be263b968f12a3125661da02b6",
                "0xf80a13f4e928017d39a00023e773fefb96237edd"
            ],
            "previous_hash":
            "394ff283d7ec4b7ac135392fccfbe59ac8c52f6a2019f7d6085ce5d9a8208b19"
        },
        "receipts": [{
            "data": {
                "block_index": 8394,
                "block_hash":
                "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
                "vote": 9,
                "timestamp": 1661510690000,
                "wallet_address": "0x70a1bc5faa2c6d996ece06a5519ecdfa0a1ad77c"
            },
            "public_key":
            "wSC2LGJhbXg+ENV5RqOOgQ1ZSFZlT406XIj8DmnJTkgi6qGY8HDq02+4MIsm5MPwGoeuNUOsY6796whiBx9XdQ==",
            "signature":
            "piDfI28xCtEmpbF26lXKAx+oMamxeJNJbhCo33+9HJ6yZH0WfMOwhIWqHgcJ0GcBfmtehmAK/idNky8NruW4iQ=="
        }, {
            "data": {
                "block_index": 8394,
                "block_hash":
                "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
                "vote": 1,
                "timestamp": 1661510690000,
                "wallet_address": "0x8aa253c22c19f8559d6de0df1cfbc053b5cb76ae"
            },
            "public_key":
            "vB8JE9Un5wxdhtsMyzpblUcm1k8aH35cnjYlpsO0clujRhlDz7BxqN28Fo1gu58hpOAUTJ3RzGXYtfmVv5M92Q==",
            "signature":
            "uqjQpNfykSE7ZJDUcTs42SfW/uTIpqYT2qFtMtjrUZtdsxc++aXEJuQOhmolKiSsqdesGj4frOPR3h6yoFsZfw=="
        }, {
            "data": {
                "block_index": 8394,
                "block_hash":
                "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
                "vote": 1,
                "timestamp": 1661510690000,
                "wallet_address": "0x293c137a8b647b59dba28265e24e9e9040daa86c"
            },
            "public_key":
            "tp9Qkg7VHdbzch5bm8rs/OUvz3rPPGO45p1BVuy6gPVFKEEpGYCoQP3ktXh8yZMbvRYtxYgSVx8p5pcJBLOTFg==",
            "signature":
            "XmUORFDaWuVF+xmWGVnqZLkn3tAxCq6uPg1XJzAp27LrjaekrWx2WwhybbJIlPziXVUsidXMrPYNwFxf5f6o2g=="
        }, {
            "data": {
                "block_index": 8394,
                "block_hash":
                "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
                "vote": 1,
                "timestamp": 1661510690000,
                "wallet_address": "0xf80a13f4e928017d39a00023e773fefb96237edd"
            },
            "public_key":
            "PRqiUuz5hNidaHzy3IzqXigyKvRgzNNzxJ1p5IgoNpqzW5zOqfNDAjpy5Fu5NnaI4rVhjcG+9uVgObo48nq5Dg==",
            "signature":
            "SihwhU2XaAuU8bwkdZeUOUBuxR9LSyyFArbgDbB+uG6S/6HR+P5dF88YmR5bA+suHmMEafsc2tNzBZ/umP+4Rw=="
        }, {
            "data": {
                "block_index": 8394,
                "block_hash":
                "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
                "vote": 1,
                "timestamp": 1661510690000,
                "wallet_address": "0xdcb66aff33c4e0f7f4f7e02f9fb7d378106a6c9d"
            },
            "public_key":
            "QxAPMi/kJqNXEb9/lBEL6r6fhJOToMQIkcMx3oVFlrtchnK6Hf5i35mBIdIL2+ntQpUIQTEftkYiJC4UzQVWMw==",
            "signature":
            "3qGXKTjH97Ek8pChk7fQQPSNqLGfvFczHkP2++ZVRl+i2nEa+mgW6qZoT22qg4BfIjTWgYU0DTQNCmyGu5SKvg=="
        }, {
            "data": {
                "block_index": 8394,
                "block_hash":
                "3bf716948c7bd307090db0151d0a4e619563a71bc40907fde70636d8fcb8cab9",
                "vote": 1,
                "timestamp": 1661510690000,
                "wallet_address": "0xf1f4e36072f485be263b968f12a3125661da02b6"
            },
            "public_key":
            "ezlZCYEVHZZaLJ5bOO6abIMZ4AVDMsbfSVnzR1XmRXLIxRJp86oLetMxwr1v6jwRI4uCP2dOWoH1t6U6FIHYDg==",
            "signature":
            "esLFgC2/+On7iW2cNH4MH3m+V5Abfx2+qsDloCBC5tV8+qawJSonNnV5mYe33hctEdRUXFOEeNRcZ+2RVssjlA=="
        }],
        "software_version":
        "1.1.1",
        "peers_already_broadcasted": [
            "52.54.229.193", "54.235.233.113", "54.156.144.119",
            "54.237.181.147", "13.127.196.33", "52.87.190.198",
            "54.89.247.181", "18.207.247.90", "18.212.52.66", "3.95.6.136",
            "44.201.107.218", "54.173.203.193", "54.224.32.13", "107.22.66.79",
            "54.209.23.25", "44.206.235.11", "43.204.238.245",
            "44.210.144.157", "54.158.89.184", "159.223.163.198",
            "52.70.231.62", "35.173.247.253", "44.201.112.134",
            "18.205.243.78", "54.167.176.113", "44.201.168.111", "52.90.6.61",
            "3.86.255.119", "34.203.202.177", "44.206.252.92", "3.86.144.115",
            "52.91.229.20", "54.89.180.51", "18.234.144.0", "3.83.212.229",
            "3.95.200.68", "3.86.87.221"
        ]
    }
    # with open('./logs/big_block_sample.json', 'r') as f:
    #     original_block = json.load(f)
    original_block_string = json.dumps(original_block)
    original_block = json.loads(original_block_string)
    compressed_block = compress_block_payload(original_block)

    decompressed_block = decompress_block_payload(compressed_block)
    compression_ratio = len(compressed_block) / len(original_block_string)
    print('Compression ration: ', compression_ratio)
    assert original_block == json.loads(json.dumps(decompressed_block))
