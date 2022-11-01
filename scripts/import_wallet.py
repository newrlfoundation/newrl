import json


if __name__ == '__main__':
  environment = input('Enter environment[mainnet/testnet/devnet]: ')

  print('This will show your private key on screen. Make sure nobody else have access to your screen.')

  wallet = input('Enter your wallet json: ')
  wallet = json.loads(wallet)
  confirm = input('This will overwrite your existing wallet if exists. Confirm to proceed with Y: ')

  if confirm == 'Y' or confirm == 'y':
    try:
      with open('data_' + environment + '/.auth.json', 'w') as f:
        json.dump(wallet, f)
    except Exception as e:
      print('Error: ', str(e))
      print(f'Please check if file data_{environment} exists')
