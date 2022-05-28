import logging
from .codes.log_config import logger_init
logger_init()
import argparse
import os
import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .codes.p2p.sync_chain import sync_chain_from_peers
from .constants import NEWRL_PORT
from .codes.p2p.peers import init_bootstrap_nodes, update_my_address, update_software
from .codes.clock.global_time import sync_timer_clock_with_global
from .codes.updater import global_internal_clock, start_miner_broadcast_clock, start_mining_clock

from .routers import blockchain, system, p2p, transport


logger = logging.getLogger(__name__)

app = FastAPI(
    title="The Newrl APIs",
    description="This page covers all the public APIs available at present in the Newrl blockchain platform."
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blockchain.router)
app.include_router(p2p.router)
app.include_router(system.router)
app.include_router(transport.router)

args = {
    'disablenetwork': False,
    'disableupdate': False,
    'disablebootstrap': False,
}

@app.on_event('startup')
def app_startup():
    try:
        if not args['disablenetwork']:
            sync_timer_clock_with_global()
            if not args['disableupdate']:
                update_software(propogate=False)
            if not args['disablebootstrap']:
                init_bootstrap_nodes()
            sync_chain_from_peers()
            update_my_address()
    except Exception as e:
        print('Bootstrap failed')
        logging.critical(e, exc_info=True)
    
    start_miner_broadcast_clock()
    global_internal_clock()
    

@app.on_event("shutdown")
def shutdown_event():
    print('Shutting down node')
    os._exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--disablenetwork", help="run the node local only with no network connection", action="store_true")
    parser.add_argument("--disableupdate", help="run the node without updating software", action="store_true")
    parser.add_argument("--disablebootstrap", help="run the node without bootstrapping", action="store_true")
    _args = parser.parse_args()
    args["disablenetwork"] = _args.disablenetwork
    uvicorn.run("app.main:app", host="0.0.0.0", port=NEWRL_PORT, reload=True)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Newrl APIs",
        version="1.0",
        description="APIs for Newrl - the blockchain platform to tokenize assets - to invest, lend and pay on-chain.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "http://newrl.net/assets/img/icons/newrl_logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
