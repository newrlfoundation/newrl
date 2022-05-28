import requests

NODE_URL = 'http://18.208.160.119:8182'
# NODE_URL = 'http://44.203.127.164:8182'


def verify_node(node_address):
  node_address = 'http://' + node_address + ':8182'
  last_block_url = node_address + '/get-last-block-index'
  print(last_block_url)
  last_block = requests.get(node_address + '/get-last-block-index', timeout=1).text
  last_block = int(last_block)

  blocks = requests.post(node_address + '/get-blocks', json={
    "block_indexes": list(range(1, last_block + 1))
  }, timeout=10).json()

  previous_hash = "0"

  for block in blocks:
    print(block['block_index'])
    if block['previous_hash'] != previous_hash:
      print('Chain invalid from index', block['block_index'])
    previous_hash = block['hash']

  print(f'{node_address} - chain is valid')


def check_block_exist(node_addr):
  url = 'http://' + node_addr + ':8182/get-block?block_index=1'
  block = requests.get(url, timeout=1).json()
  if 'block_index' not in block:
    # print(f'{node_addr} - Invalid')
    print(f'{node_addr} - Reverting')
    requests.post('http://' + node_addr + ':8182/revert-chain?block_index=0&propogate=false', timeout=1).json()
    requests.post('http://' + node_addr + ':8182/sync-chain-from-peers', 
      json={
        "block_index": 0
      }, timeout=1).json()


for node in ['100.27.31.95', '13.127.196.33', '18.205.152.148', '18.205.189.2', '18.206.94.76', '18.207.216.103', '18.208.182.177', '18.212.66.84', '184.72.208.65', '3.80.209.8', '3.83.50.130', '3.84.50.209', '3.84.77.114', '3.86.220.174', '3.86.95.36', '3.87.215.96', '3.87.239.9', '3.87.59.246', '3.89.74.97', '3.89.88.60', '3.91.148.23', '3.91.240.161', '3.94.187.48', '34.230.43.253', '34.238.254.65', '35.171.16.241', '35.175.149.140', '44.201.104.135', '44.201.195.243', '44.202.100.22', '44.202.112.192', '44.202.36.179', '44.202.6.221', '44.203.125.108', '44.203.155.59', '44.204.232.32', '44.204.33.70', '52.203.35.134', '52.207.247.190', '52.23.232.237', '52.87.240.182', '52.90.193.227', '52.91.186.245', '52.91.72.62', '52.91.72.92', '54.158.53.69', '54.164.113.49', '54.164.15.194', '54.165.186.46', '54.173.64.147', '54.175.45.195', '54.197.74.80', '54.209.119.94', '54.209.184.138', '54.209.95.85', '54.210.130.74', '54.224.29.208', '54.237.250.151', '54.84.93.34', '54.85.121.224', 'testnet.newrl.net']:
  try:
    check_block_exist(node)
  except:
    pass
    # print(f'{node} - Unreachable')
