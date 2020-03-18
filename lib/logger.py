import logging
import os

from lib.constant import APP_ROOT_DIR

logFileDir = APP_ROOT_DIR + "/log"
if not os.path.isdir(logFileDir):
    os.makedirs(logFileDir)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.basicConfig(filename=logFileDir + '/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def get_logger(name=None):
    if name is None:
        name = __name__

    return logging.getLogger(name)
