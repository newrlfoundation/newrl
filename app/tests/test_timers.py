import time

from .test_p2p import _receive_block
from .test_miner_committee import _add_test_miner
from ..codes.updater import start_mining_clock
from ..codes.minermanager import broadcast_miner_update
from fastapi.testclient import TestClient
from ..constants import BLOCK_TIME_INTERVAL_SECONDS

from ..main import app
from app.codes import updater

client = TestClient(app)


def test_mining_clock():
    broadcast_miner_update()
    updater.mine(True)

    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    previous_block_index = int(response.text)

    # start_mining_clock()

    # time.sleep(BLOCK_TIME_INTERVAL_SECONDS + 2)

    # response = client.get('/get-last-block-index')
    # assert response.status_code == 200
    # block_index = int(response.text)

    # assert block_index == previous_block_index + 2

    # for i in range(1, 3):
    #     _add_test_miner(i)
    # time.sleep(BLOCK_TIME_INTERVAL_SECONDS * 4)
    # os._exit(1)


# def test_all_timers():
#     broadcast_miner_update()
#     updater.mine(True)

#     broadcast_miner_update()
#     updater.mine(True)
    
#     response = client.get('/get-last-block-index')
#     assert response.status_code == 200
    
#     previous_block_index = int(response.text)
#     _receive_block(previous_block_index + 1)