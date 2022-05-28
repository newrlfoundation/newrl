## my_logger.py
from datetime import datetime
import time
import os
import pathlib
## Init logging start 
import logging
import logging.handlers
from sh import tail
from sse_starlette.sse import EventSourceResponse

'''Logger Config and Foramtters'''

path = "logs/"
filename = "newrl-node-log"

def logger_init():
    logger = logging.getLogger() ## root logger
    logger.setLevel(logging.INFO)

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    logfilename = filename
    file = logging.handlers.RotatingFileHandler(f"{path}{logfilename}", backupCount= 25, maxBytes= 2*1000*1000)
    fileformat = logging.Formatter("%(asctime)s [%(levelname)s]: %(name)s: %(message)s")
    file.setLevel(logging.INFO)
    file.setFormatter(fileformat)

    stream = logging.StreamHandler()
    streamformat = logging.Formatter("%(asctime)s [%(levelname)s]: %(name)s: %(message)s")
    stream.setLevel(logging.INFO)
    stream.setFormatter(streamformat)

    if (logger.hasHandlers()):
        logger.handlers.clear()

    logger.addHandler(file)
    logger.addHandler(stream)


def logger_cleanup(path, days_to_keep):
    lclogger = logging.getLogger(__name__)
    logpath = f"{path}"
    now = time.time()
    for filename in os.listdir(logpath):
        filestamp = os.stat(os.path.join(logpath, filename)).st_mtime
        filecompare = now - days_to_keep * 86400
        if  filestamp < filecompare:
            lclogger.info("Delete old log " + filename)
            try:
                os.remove(os.path.join(logpath, filename))
            except Exception as e:
                lclogger.exception(e)
                continue

'''Log Streaming Methods'''

async def logGenerator(request):
    logfilename = filename
    logFile = f"{path}{logfilename}"
    for line in tail("-f", logFile, _iter=True):
        if await request.is_disconnected():
            print("client disconnected!")
            break
        yield line
        time.sleep(0.9)


def get_past_log_content(filename=filename):
    # if filename is None:
    logfilename = datetime.now().strftime("%Y%m%d_%H") + f"_{filename}"
    logFile = f"{path}{logfilename}"
    with open(logFile) as f:
        return f.read()
