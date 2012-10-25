
import os
import appsettings
import re
import sys
from django.core.management import setup_environ

sys.path.append(os.path.realpath(".."))
import settings
setup_environ(settings)



filename = re.compile("__init__|test")

for package in appsettings.MODEL_DEFINITION :
    try :
        modules = os.listdir(os.path.join(appsettings.APP_PATH,
                                          package.replace(".", os.sep)))
        for module in modules:
            (name, ext) = os.path.splitext(module)
            if filename.search(name) or ext == ".pyc":
                continue
            module = __name__ + "." + package + "." + name
#            print "Trying to import %s" % (module)
            __import__(module)

    except Exception as e:
        raise





