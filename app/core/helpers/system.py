import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)


def update_and_restart():
    logger.info('Updating and restarting')
    subprocess.call(["sh", "scripts/install.sh"])
    os.execv(sys.executable, ['python', '-m', 'app.main'] + sys.argv[1:])
