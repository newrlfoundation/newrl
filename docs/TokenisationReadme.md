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