'''
Created on Jun 14, 2012

@author: fredo
'''

import logging
from django.conf import settings

nametologger = {}

def getLogger(name):
    try:
        logger = nametologger[name]
        return logger
    except KeyError:
        logger = logging.getLogger(name)
        handler = logging.FileHandler(filename=settings.LOG_PATH)
        handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        nametologger[name] = logger
        return logger
