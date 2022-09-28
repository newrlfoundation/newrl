import json


if __name__ == '__main__':
  environment = input('Enter environment[mainnet/testnet/devnet]: ')

  print('This will show your private key on screen. Make sure nobody else have access to your screen.')
  confirm = input('Confirm to proceed with Y: ')

  if confirm == 'Y' or confirm == 'y':
    try:
      with open('data_' + environment + '/.auth.json', 'r') as f:
        auth_file = json.load(f)
        print(json.dumps(auth_file['wallet']))
    except Exception as e:
      print('Error: ', str(e))
      print('Error retrieving wallet. Make sure you have the right environment installed and wallet file is valid')
      print(f'Please check if file data_{environment} exists')
