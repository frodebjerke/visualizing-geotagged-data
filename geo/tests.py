"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""


import appsettings
import os
import sys
import re
import logging

logger = logging.getLogger(__name__)

def loaddefinitions(packages, importall = False, nglobals = globals()):
    " Import every module in packages or import every definition from every module in packages. Probably not compatible with nested packages."  
    
    filename = re.compile("__init__|test")
    
    for package in packages:
        try :
            modulepaths = os.listdir(os.path.join(appsettings.APP_PATH,
                                              package.replace(".", os.sep)))
            for modulepath in modulepaths:
                (name, ext) = os.path.splitext(modulepath)
                if filename.search(name) or ext == ".pyc":
                    continue
                modulename = appsettings.APP_NAME + "." + package + "." + name
                logger.debug("Trying to import %s" % (modulename))
                __import__(modulename)
                if importall:
                    module = sys.modules[modulename]
                    for k in dir(module):
#                        print k
                        nglobals[k] = module.__dict__[k]
    
    
        except Exception as e:
            raise

def loadmodels():
    loaddefinitions(packages = appsettings.MODEL_DEFINITION)

def loadtests(nglobals):
    loaddefinitions(packages = appsettings.TEST_DEFINITION, nglobals = nglobals, importall = True)

loadtests(nglobals = globals())

#from geo.map.maptest import MapTest 
#from geo.coordinate.gpxtest import GPXTest
#from geo.video.oggtest import OggTest
