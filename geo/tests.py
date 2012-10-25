"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import settings
from appsettings import APP_PATH, APP_NAME
import unittest
import os
import re
import types
import unittest

base = os.path.split(__file__)[0]
filetest = re.compile("test\.py$")


def loadtests(path):
    global filetest
    for dirpath, dirnames, filenames in os.walk(path):
        tests = [filename for filename in filenames
                     if filetest.search(filename)]
        for test in tests:
            modulename = tomodulename(test, dirpath)

            module = __import__(modulename)
            for attr in dir(module):
                if attr == types.ClassType and issubclass(attr, unittest.TestCase):
                    print "Importing %s " % attr
                    __import__(module, attr)

def tomodulename(filename, dirpath):
    global base
    filename = filename.replace(".py", "")
    modulename = os.path.join(dirpath.replace(base, ""), filename)
    split = modulename.split("/")
    if split[0] == "":
        split = split[1:]
    split.insert(0, APP_NAME)
    modulename = ".".join(split)
    return modulename

loadtests(base)

from geo.map.maptest import MapTest
from geo.coordinate.gpxtest import GPXTest
from geo.video.oggtest import OggTest
