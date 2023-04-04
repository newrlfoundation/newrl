import logging

from app.config.Configuration import Configuration
from app.core.clock.timers import TIMERS
from .core.helpers.log_config import logger_init
logger_init()
import argparse
import os
import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler

from .core.p2p.sync_chain import sync_chain_from_peers
from .config.constants import NEWRL_PORT, IS_TEST
from .core.p2p.peers import init_bootstrap_nodes, update_my_address, update_software
from .core.clock.global_time import sync_timer_clock_with_global
from .core.blockchain.updater import am_i_sentinel_node, global_internal_clock, start_miner_broadcast_clock, start_mining_clock

from .routers import blockchain, system, p2p, transport
from .core.helpers.limiter import limiter


logger = logging.getLogger(__name__)

app = FastAPI(
    title="The Newrl APIs",
    description="This page covers all the public APIs available at present in the Newrl blockchain platform."
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blockchain.router)
app.include_router(p2p.router, include_in_schema=False)
app.include_router(system.router, include_in_schema=False)
app.include_router(transport.router, include_in_schema=False)
def initialze_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("--disablenetwork", help="run the node local only with no network connection",
                        action="store_true")
    parser.add_argument("--disableupdate", help="run the node without updating software", action="store_true")
    parser.add_argument("--disablebootstrap", help="run the node without bootstrapping", action="store_true")
    parser.add_argument("--fullnode", help="run a full/archive node", action="store_true")
    parser.add_argument("--noreload", help="no auto-reload from code", action="store_true")
    _args, unknown = parser.parse_known_args()
    args = {
        'disablenetwork': _args.disablenetwork,
        'disableupdate': _args.disableupdate,
        'disablebootstrap': _args.disablebootstrap,
        'fullnode': _args.fullnode,
        'noreload': _args.noreload,
    }
    return args

try:
    args = initialze_params()
    logger.info('Running with arguments: ' + str(args))
except Exception as e:
    logger.error('Cannot parse params: ' + str(e))
    args = {
        'disablenetwork': False,
        'disableupdate': False,
        'disablebootstrap': False,
        'fullnode': False,
        'noreload': False,
    }
Configuration.conf['FULL_NODE'] = args["fullnode"]


@app.on_event('startup')
def app_startup():
    try:
        logger.info("Initializing Config Values")
        Configuration.init_values()
        Configuration.init_values_in_db()
        if not IS_TEST:
            sync_timer_clock_with_global()
            init_bootstrap_nodes()
            sync_chain_from_peers()
            update_my_address()
    except Exception as e:
        logger.error('Bootstrap failed')
        logging.critical(e, exc_info=True)

    if not IS_TEST:
        if not am_i_sentinel_node():
            logger.info('Participating in mining')
            start_miner_broadcast_clock()
        else:
            logger.info('Not participating in mining')


        global_internal_clock()
    

@app.on_event("shutdown")
def shutdown_event():
    print('Shutting down node and stopping timers')
    try:
        TIMERS['global_timer'].cancel()
    except:
        pass
    os._exit(0)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=NEWRL_PORT, reload=False)




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
