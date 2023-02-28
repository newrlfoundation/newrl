import os

from app.config.ntypes import NEWRL_TOKEN_DECIMAL


NEWRL_ENV = os.environ.get('NEWRL_ENV')

if NEWRL_ENV == 'testnet':
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
    TREASURY_WALLET_ADDRESS = '0x1111111111111111111111111111111111111111'
    NETWORK_TRUST_MANAGER_WALLET = '0x1111111111111111111111111111111111111112'
    NETWORK_TRUST_MANAGER_PID = 'pi1111111111111111111111111111111111111112'
    ASQI_PID = 'pi1111111111111111111111111111111111111114'
    ASQI_WALLET = '0xce4b9b89efa5ee6c34655c8198c09494dc3d95bb'
    ASQI_WALLET_PUBLIC = 'f9a8e9773c706a6c32182144dd656409853b7eb25782ba61e5b9030ae19baf63fea3672464496e8ac4ac7046bedcbe7ae9f1d20481fcbceefc22afdfbf14ee27'
    ASQI_WALLET_DAO = ASQI_WALLET
    FOUNDATION_PID = 'pi1111111111111111111111111111111111111113'
    SENTINEL_PID = 'pi1111111111111111111111111111111111111121'
    FOUNDATION_WALLET = '0xce6124c19691a2f140f141705ce1791d45c347a5'
    FOUNDATION_WALLET_PUBLIC = '5836e0dfd772050c5cb807f36dfe5a65ff2234ad0723e52c42e1d6fddb0aca7d68718a500ef63caa4641044d73b6b7ecc05091bb2ca2cd7b7061164a262b5d95'
    FOUNDATION_WALLET_DAO = FOUNDATION_WALLET
    SENTINEL_NODE_WALLET = '0xd6c038f5c25dae8a8f7350a58fb79ef0c3c625a5'
    SENTINEL_NODE_WALLET_PUBLIC = 'fb4d35cb763fdc415323280155ffc14eabb40fd473f833b85aa6fd0aeb68eabea9a706bddf84267866af758d1c31596492154353ebc359150536606d44dc2368'
    DAO_MANAGER = 'ct9000000000000000000000000000000000000da0'
    NETWORK_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111112'
    FOUNDATION_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111113'
    ASQI_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111114'
    ASQI_DAO_ADDRESS = 'ctda01111111111111111111111111111111111114'
    CUSTODIAN_DAO_ADDRESS = 'ctda01111111111111111111111111111111111da0'
    FOUNDATION_DAO_ADDRESS = 'ctda01111111111111111111111111111111111113'
    CONFIG_DAO_ADDRESS = 'ct1111111111111111111111111111111111111111'
    STAKE_COOLDOWN_MS = 600000
    MIN_STAKE_AMOUNT = 500000 * pow(10, NEWRL_TOKEN_DECIMAL)
    STAKE_PENALTY_RATIO = 10
    STAKE_CT_ADDRESS = 'ct1111111111111111111111111111111111111115'
    MEMBER_WALLET_LIST = [
        '0xf98eafede44ae6db2f6e6ad3762f5419ff1196d9',
        '0x9dd356a2e4aa9a6c182d5f1e3f2e40ffa27bcfd5',
        '0x47538e46a78e729079eb1614e2d6c387119c21fa',
        '0x1342e0ae1664734cbbe522030c7399d6003a07a8',
        '0x495c8153f65cf402bb0af6f93ba1eed4ace9aa7f',
        '0x52c3a0758644133fbbf85377244a35d932443bf0',
        '0x5017b00ced00b8b51d77d4569fa9d611b5b3b77a'
    ]
    CUSTODIAN_WALLET_LIST = MEMBER_WALLET_LIST + [
        'ct9000000000000000000000000000000000000da0',
        CUSTODIAN_DAO_ADDRESS,
        ASQI_WALLET,
        FOUNDATION_WALLET,
    ]
elif NEWRL_ENV == 'mainnet':
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
    TREASURY_WALLET_ADDRESS = '0x1111111111111111111111111111111111111111'
    NETWORK_TRUST_MANAGER_WALLET = '0x1111111111111111111111111111111111111112'
    NETWORK_TRUST_MANAGER_PID = 'pi1111111111111111111111111111111111111112'
    ASQI_PID = 'pi1111111111111111111111111111111111111114'
    ASQI_WALLET = '0x05265ea663b4957281cce80e5417bb969b2d21be'
    ASQI_WALLET_PUBLIC = '1d5959b2e189621f1164c41e823f6fc3377ef21edfcf0ad271ef7bee4d007f7d55e20c1d0a8a56952863837e1d517235c86253281da1a8d1af79c1d8fa705a68'
    ASQI_WALLET_DAO = ASQI_WALLET
    FOUNDATION_PID = 'pi1111111111111111111111111111111111111113'
    FOUNDATION_WALLET = '0x8f5708d44c6340f31f6401ddff9fb6524eeddc95'
    FOUNDATION_WALLET_PUBLIC = 'ffc0f9455f34cffe14b8a268edef48fd651a7510e520c98b722db2050be688e127e83e0b42dc10cc40da35f94d48d9cc4df531eaebf450725d58015b7d060e87'
    FOUNDATION_WALLET_DAO = FOUNDATION_WALLET
    SENTINEL_PID = 'pi1111111111111111111111111111111111111121'
    SENTINEL_NODE_WALLET = '0x5dbbe6cdf5022c4b331d078c9e93e40457d348d2'
    SENTINEL_NODE_WALLET_PUBLIC = 'ba126d3d5db311c017341c9fe4b99f36fe30fdda9b80680463eb8a1f6e2b9e25b496b23784555e4606390db08bec115c0e7be3035d0f77c8f281f2afe5b828a9'
    DAO_MANAGER = 'ct9000000000000000000000000000000000000da0'
    NETWORK_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111112'
    FOUNDATION_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111113'
    ASQI_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111114'
    ASQI_DAO_ADDRESS = 'ctda01111111111111111111111111111111111114'
    CUSTODIAN_DAO_ADDRESS = 'ctda01111111111111111111111111111111111da0'
    FOUNDATION_DAO_ADDRESS = 'ctda01111111111111111111111111111111111113'
    CONFIG_DAO_ADDRESS = 'ct1111111111111111111111111111111111111111'
    STAKE_COOLDOWN_MS = 600000
    MIN_STAKE_AMOUNT = 500000 * pow(10, NEWRL_TOKEN_DECIMAL)
    STAKE_PENALTY_RATIO = 10
    STAKE_CT_ADDRESS = 'ct1111111111111111111111111111111111111115'
    MEMBER_WALLET_LIST = [
        '0xe6a8c8c7f3629ec13648ed56707328032283301d',
        '0xed73ff44188695f9d7ef4c658363620378328db6',
        '0xf730cf246b1b378ff64335df13dfa8cad3c82c97',
        '0xff6bdaff96277f3ad7c939cf49520462fbeda8e5',
        '0x86aef7b61a68e84eb5d62cc74dd3e01590f52980',
        '0xea6471d911bf54d877afa084aa4959674183128b',
        '0xa779193a823690768de7dd17be49ff4b2e042dd8'
    ]
    CUSTODIAN_WALLET_LIST = MEMBER_WALLET_LIST + [
        'ct9000000000000000000000000000000000000da0',
        CUSTODIAN_DAO_ADDRESS,
        ASQI_WALLET,
        FOUNDATION_WALLET,
    ]
else:
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
    TREASURY_WALLET_ADDRESS = '0x1111111111111111111111111111111111111111'
    NETWORK_TRUST_MANAGER_WALLET = '0x1111111111111111111111111111111111111112'
    NETWORK_TRUST_MANAGER_PID = 'pi1111111111111111111111111111111111111112'
    ASQI_PID = 'pi1111111111111111111111111111111111111114'
    ASQI_WALLET = '0xce4b9b89efa5ee6c34655c8198c09494dc3d95bb'
    ASQI_WALLET_PUBLIC = 'f9a8e9773c706a6c32182144dd656409853b7eb25782ba61e5b9030ae19baf63fea3672464496e8ac4ac7046bedcbe7ae9f1d20481fcbceefc22afdfbf14ee27'
    ASQI_WALLET_DAO = ASQI_WALLET
    FOUNDATION_PID = 'pi1111111111111111111111111111111111111113'
    FOUNDATION_WALLET = '0xce6124c19691a2f140f141705ce1791d45c347a5'
    FOUNDATION_WALLET_PUBLIC = '5836e0dfd772050c5cb807f36dfe5a65ff2234ad0723e52c42e1d6fddb0aca7d68718a500ef63caa4641044d73b6b7ecc05091bb2ca2cd7b7061164a262b5d95'
    FOUNDATION_WALLET_DAO = FOUNDATION_WALLET
    SENTINEL_PID = 'pi1111111111111111111111111111111111111121'
    SENTINEL_NODE_WALLET = '0xd6c038f5c25dae8a8f7350a58fb79ef0c3c625a5'
    SENTINEL_NODE_WALLET_PUBLIC = 'fb4d35cb763fdc415323280155ffc14eabb40fd473f833b85aa6fd0aeb68eabea9a706bddf84267866af758d1c31596492154353ebc359150536606d44dc2368'
    DAO_MANAGER = 'ct9000000000000000000000000000000000000da0'
    NETWORK_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111112'
    FOUNDATION_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111113'
    ASQI_TREASURY_ADDRESS = 'ct1111111111111111111111111111111111111114'
    ASQI_DAO_ADDRESS = 'ctda01111111111111111111111111111111111114'
    CUSTODIAN_DAO_ADDRESS = 'ctda01111111111111111111111111111111111da0'
    FOUNDATION_DAO_ADDRESS = 'ctda01111111111111111111111111111111111113'
    CONFIG_DAO_ADDRESS = 'ct1111111111111111111111111111111111111111'
    STAKE_COOLDOWN_MS = 600000
    MIN_STAKE_AMOUNT = 500000 * pow(10, NEWRL_TOKEN_DECIMAL)
    STAKE_PENALTY_RATIO = 10
    STAKE_CT_ADDRESS = 'ct1111111111111111111111111111111111111115'
    MEMBER_WALLET_LIST = [
        '0xf98eafede44ae6db2f6e6ad3762f5419ff1196d9',
        '0x9dd356a2e4aa9a6c182d5f1e3f2e40ffa27bcfd5',
        '0x47538e46a78e729079eb1614e2d6c387119c21fa',
        '0x1342e0ae1664734cbbe522030c7399d6003a07a8',
        '0x495c8153f65cf402bb0af6f93ba1eed4ace9aa7f',
        '0x52c3a0758644133fbbf85377244a35d932443bf0',
        '0x5017b00ced00b8b51d77d4569fa9d611b5b3b77a'
    ]
    CUSTODIAN_WALLET_LIST = MEMBER_WALLET_LIST + [
        'ct9000000000000000000000000000000000000da0',
        CUSTODIAN_DAO_ADDRESS,
        ASQI_WALLET,
        FOUNDATION_WALLET,
    ]