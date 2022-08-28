from fastapi import APIRouter
from starlette.requests import Request
from app.codes.p2p.packager import decompress_block_payload
from app.codes.p2p.transport import receive
from app.codes.p2p.sync_chain import receive_block

router = APIRouter()

transport_tag = 'Transport'


@router.post("/receive", tags=[transport_tag])
def recieve_api(payload: dict):
    return receive(payload)

@router.post("/receive-block-binary", tags=[transport_tag])
async def receive_block_binary_api(req: Request):
    body = req.body()
    block = decompress_block_payload(await body)
    return receive_block(block)
