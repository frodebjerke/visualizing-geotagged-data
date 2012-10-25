'''
Created on Mar 20, 2012

@author: fredo
'''

from unittest import TestCase
from geo.video.ogg import Ogg
from settings import TEST_PATH
import os
import time

class OggTest(TestCase):
    
    
    TEST_FILE_NAME = "video"
    EXTENSIONS = [".ogv",".avi",".3gp",".swf",".mpeg"]
    SLEEP_DURATION = 10
    
    def setUp(self):
        self.createpaths()
        pass
    
    def createpaths(self):
        self.paths = []
        for extension in self.EXTENSIONS:
            self.paths.append([os.path.join(TEST_PATH,
                                           self.TEST_FILE_NAME+extension),
                               os.path.join(TEST_PATH,
                                            self.TEST_FILE_NAME+extension.replace(".","_")+"_out"+Ogg.EXT)])
            
    def testconvert(self):
        for source,target in self.paths:
            ogg = Ogg()
            print "Start conversion of %s" % (source,)
            source = open(source,"rb")
            ogg.convert(source,target)
            while not ogg.isfinished():
                print "Going to sleep for %d" % (self.SLEEP_DURATION,)
                time.sleep(self.SLEEP_DURATION)
            self.assertEquals(ogg.getexitcode(),0,"Conversion exit status should be 0")
            self.assertTrue(os.path.exists(target),"Converted video should exist")
            os.remove(target)
            temppath = ogg.temppath
            ogg = None
            self.assertFalse(os.path.exists(temppath), "Temp file from converter should be deleted")
            