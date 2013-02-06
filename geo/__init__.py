import os
import appsettings
import re
import sys
import appsettings



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
#                print "Trying to import %s" % (modulename)
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


