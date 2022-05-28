from fastapi import APIRouter
from app.codes.p2p.transport import receive

router = APIRouter()

transport_tag = 'Transport'


@router.post("/receive", tags=[transport_tag])
def recieve_api(payload: dict):
    return receive(payload)
