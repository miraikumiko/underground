import logging
import libvirt
from src.config import LOG_PATH

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

if not LOG_PATH or LOG_PATH == '':
    LOG_PATH = "/dev/null"

fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter(
    "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)


# Disable libvirt error messages in console

def libvirt_callback(*args):
    pass

libvirt.registerErrorHandler(libvirt_callback, None)
