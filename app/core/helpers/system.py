import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)


def update_and_restart(env):
    logger.info('Updating and restarting for '+env )
    subprocess.call(["sh", "scripts/install.sh",env])
    os.execv(sys.executable, ['python', '-m', 'app.main'] + sys.argv[1:])