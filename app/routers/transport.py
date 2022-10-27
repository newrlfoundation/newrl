from fastapi import APIRouter
from starlette.requests import Request
from app.codes.p2p.packager import decompress_block_payload
from app.codes.p2p.transport import receive
from app.codes.p2p.sync_chain import receive_block
from app.limiter import limiter

router = APIRouter()

transport_tag = 'Transport'


@router.post("/receive", tags=[transport_tag], include_in_schema=False)
def recieve_api(payload: dict):
    return receive(payload)

@router.post("/receive-block-binary", tags=[transport_tag], include_in_schema=False)
@limiter.limit("10/minute")
async def receive_block_binary_api(request: Request):
    body = request.body()
    block = decompress_block_payload(await body)
    return receive_block(block)
