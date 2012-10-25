'''
Created on Mar 22, 2012

@author: fredo
'''

class TracePointDTO:
    def __init__(self,lat,lon,realtime,videotime,video,address = None):
        self.lat = lat
        self.lon = lon
        self.realtime = realtime
        self.videotime = videotime
        self.video = video
        self.address = address

    def getlat(self):
        return self.lat
    def getlon(self):
        return self.lon
    def getrealtime(self):
        return self.realtime
    def getvideotime(self):
        return self.videotime
    def getvideo(self):
        return self.video
    def getaddress(self):
        return self.address