import logging
from os import getenv

from k8spin_operator.handlers import *

logger = logging.getLogger()
logger.setLevel(getenv("LOGGING_LEVEL", "INFO"))
