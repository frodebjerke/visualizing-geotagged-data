'''
Created on Mar 19, 2012

@author: fredo
'''

from geo.video.profile import Profile

class Converter:
    
    profile = Profile.VIDEOBIN
    
    def __init__(self,profile = None):
        self.setProfile(Profile.VIDEOBIN)
        pass
    
    def setProfile(self,profile):
        self.profile = profile
        
    
    def convert(self,source,targetPath):
        pass
    
    def isfinished(self):
        if self.process and self.process.poll() != None:
            return True
        else:
            return False
    
    def getexitcode(self):
        if self.process:
            return self.process.poll()
        else:
            return None
        