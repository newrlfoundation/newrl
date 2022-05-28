import requests
from app.codes.p2p.sync_mempool import receive_transaction
from app.constants import TRANSPORT_SERVER


def receive(payload):
    try:
        operation = payload['operation']
        data = payload['data']

        if operation == 'send_transaction':
            receive_transaction(data)
        elif operation == 'send_block':
            print('Received block', data)
        else:
            print('Unknown operation', operation)
    except Exception as e:
        print(e)
        return 'Invalid payload'


def send(payload):
    response = requests.post(TRANSPORT_SERVER + '/send', json=payload)
    if response.status_code != 200:
        print('Error sending')
    return response.text
