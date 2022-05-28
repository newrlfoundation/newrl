### API calls for tokenizing and transacting an asset in order

1. New partner addition (done by ASQI): output is a wallet file handed over to the partners that they can use for further wallet addition and token creation as below
2. /add-wallet[[TestNet]](https://testnet.newrl.net:8090/docs#/default/add_wallet_api_add_wallet_post)
Add new user wallet with new partner wallet from step 1 as the custodian wallet and KYC docs (can be dummy docs for test purposes but some files  are required)
This returns a transaction file for the add wallet transaction.
3. /sign[[TestNet]](https://testnet.newrl.net:8090/docs#/default/sign_sign_post)
Sign the wallet creation transaction using new partner wallet from step 1. This requires uploading the full wallet file received from asqi. 
4. /get-wallet-file[[TestNet]](https://testnet.newrl.net:8090/docs#/default/get_wallet_file_get_wallet_file_post)
Use the transaction file obtained in step 2 to get the user wallet file. Note down the wallet address from this file. This address can be used for making this user the first owner, or enabling transfers where this user is one of the parties. 
5. /create-token[[TestNet]](https://testnet.newrl.net:8090/docs#/default/create_token_create_token_post)
Create a token requires some details about the token, a custodian and first owner. Use the new partner wallet from step 1 as the custodian wallet, first owner can be any valid wallet including the same as the custodian. The returned create_token_transaction file contains the tokencode which is needed for transfer and get-balance.
6. /sign[[TestNet]](https://testnet.newrl.net:8090/docs#/default/sign_sign_post)
Sign the token creation transaction using the wallet file of whoever has been named as custodian. 
7. /run-updater [[TestNet]](https://testnet.newrl.net:8090/docs#/default/run_updater_run_updater_post)
Periodically run by scheduler but can be explicitly invoked to include new transactions to chain.
8. /get-balance[[TestNet]](https://testnet.newrl.net:8090/docs#/default/get_balance_get_balance_post)
Get balance for token in wallet
9. /create-transfer[[TestNet]](https://testnet.newrl.net:8090/docs#/default/create_transfer_create_transfer_post)
To transfer tokens from one wallet to another
10. /sign[[TestNet]](https://testnet.newrl.net:8090/docs#/default/sign_sign_post)
A transfer created at previous step need to be signed with custodian wallet


### Newrl Field Descriptions

### /add-wallet
    custodian_address - Address of the custodian creating the wallet
    ownertype - Type of wallet holder. A list is available in the conventions doc.
    jurisdiction - The phone code country in which the wallet is registered. Used for legal validations. List available in conventions doc.
    kyc_docs - An array of KYC doc objects and their hashes. List available in conventions doc.
                The hash is a hashcode of the digital file to prove the identity incase an investigation on the wallet arises.
    specific_data - A dictionary containing specific data related to the wallet being created. 
                    The application can decide what to include in here for future reference of wallet. 
                    Example can be - user_type, application level user_id or email
    public_key - The public key for which the wallet is being added. This can be obtained using /generate-wallet-address API

### /add-token
    token_name - A name or description of the token being created
    token_code - A unique code for the new token being created. The application should check first if the token code being created
                does not exist on chain. An example code for a residential property tokenised is - HSEBLR20220421
    token_type - Type of token. Allowed list available in conventions doc.
    first_owner - Wallet in which the token will be first issued.
    custodian - Custodian creating the token.
    legal_doc - Hash of the digital file of doc with binding contract for the token.
    amount_created - Quantity of tokens created
    value_created - Deprecated. To be removed.
    tokendecimal - Decimal places for the token. Example a token with tokendecimal as 3 with amount_created as 1000 will be considered 
                    as 1 quantity. 
    disallowed_regions - a list of jurisdictions of wallets which cannot hold the token.   
                Example - ["910"] means Indian wallets cannot hold this token.
    is_smart_contract_token - A flag for token to be used by smart contract. Default to false. Not to be used by apps directly.
    token_attributes - Metadata about a token. For a property token, this can contain the address, area, build etc.


### /add-transfer
    transfer_type - can be 4 or 5. 4 for bilateral transfer, 5 for unilateral transfer.
    wallet1_address - The sender for asset1_code. 
    wallet2_address - The sendr for asset2_code
    asset1_code - Token code for first asset
    asset2_code - Token code for second asset
    asset1_qty - Quantity for first asset
    asset2_qty - Quantity for second asset
    description - Any string description for the transfer.
    additional_data - Metadata about the transfer. This is mostly used by system transfers.


### Conventions used for wallet jurisdictions, token types, transaction types etc.

#### Wallets
1. Jurisdiction
    0 Undefined
    1 On-chain entity on Newrl
    2-99 reserved for on-chain entity types in future including those on non-Newrl
    chains (e.g. DAO on Ethereum)
    Standard convention: ISD code + 0 for two-digit ISD codes and ISD code itself for
    3-digit
    910 India
    440 UK
    970 Indonesia
    971 UAE
    972 Israel
    852 Hong Kong
    650 Singapore
    etc
    Exceptions: (1 digit codes)
    101 US
    199 Canada
    Exceptions: (3 digit codes with 0 at the end)
    TBD
    Any jurisdiction that needs to be isolated from kyc point of view but does not have
    separate isd code will be added above. Typically with a 3 digits code close to an
    existing code for the nearest already coded jurisdiction e.g. british virgin islands
    should be close to 440 if it does not have a separate isd)
2. Type of person
    a. Undefined: 0
    b. DAO on Newrl: 9
    i. Smart contract on Newrl: 91
    ii. DAO LLC in US: 95
    c. Natural person: 1
    d. Private company: 2
    i. Variations in private company to be 21 - 29
    e. Public and listed company: 3
    i. Variations in public company to be 31 - 39
    f. (Unlimited liability) partnership: 4
    i. Variations in unlimited liability partnership to be 41-49
    g. Limited liability partnership: 5
    i. Variations in LLP to be 51-59
    h. Trust: 6
    i. Variations in trust to be 61-69
    i. Other: 8
    i. Variations in others to be 81-89
3. Document types
    1. Tax id doc
    2. Doc for social security number / Aadhar / Similar number
    3. Passport
    4. Driving license
    5. Birth certificate
    6. Utility bill
    7. Bank statement / letter
    8. x
    9. x
    10. x
    11. Incorporation certificate
    12. Corporate tax certificate other than primary tax id
    13. X
    14. X
    15. x
#### Tokens
    0 platform token (utility as well as governance, includes NWRL token)
    1 Smart Money Token
    2-9 Other variants of SMT
    11 IOU
    12-19 Other variants of IOU
    31 Simple bonds
    32-39 Other variants of simple bonds
    41 Common stock
    42-49 Other variants of equity
    51 ETF
    52 Mutual fund
    53-59 Other variants of managed funds
    61 Unsecured loan
    62 Secured loan
    63 Convertible loan
    64-69 other varieties of loan
    71 Residential real estate
    72 Commercial real estate
    73 Land
    74 Industrial real estate
    75 Warehouse
    76 Agricultural land
    77-79 Other types of real estate
    81 Warehouse receipt of agricultural commodities
    82 WHR of base metals
    83 WHR of gold
    84 WHR of precious metals other than gold
    85 WHR of diamonds and precious stones
    91 Brand ownership
    92-94 Brand specific other tokens
    101 Generic contract with cash-flows
    102 Lease or rent contract
    103-109 various contract types
    111 Intellectual property rights
    121 Carbon credits