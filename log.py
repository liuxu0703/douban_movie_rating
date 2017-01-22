# -*- coding: utf-8 -*-
# author: liuxu

import logging
import config

logger = logging.getLogger("dmr")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
fh = logging.FileHandler(config.getLogPath())
fh.setFormatter(formatter)

if (config.debug()):
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
else:
    fh.setLevel(logging.INFO)


logger.addHandler(fh)
logger.propagate = config.debug()

def d(msg):
    logger.log(logging.DEBUG, msg)

def i(msg):
    logger.log(logging.INFO, msg)

def w(msg):
    logger.log(logging.WARN, msg)

def e(msg):
    logger.log(logging.ERROR, msg)

