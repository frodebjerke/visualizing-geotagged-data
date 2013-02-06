'''
Created on Oct 28, 2012

@author: fredo
'''
from django.db import models
from util import ConnectionMode
from geo.models import Video
from decimal import Decimal
import math

#===============================================================================
# abstract super class
#===============================================================================
class Point(models.Model):
    
    #radius of what is considered near in different transportation modes
    IS_NEAR = ((ConnectionMode.WALK,30),
               (ConnectionMode.BIKE,60),
               (ConnectionMode.MOTOR_VEHICLE,200),
               (ConnectionMode.TRAIN,1000))
    

    class Meta:
        app_label ="geo"
        abstract = True
        
#===============================================================================
# implementation
#===============================================================================

class MapPoint(Point):

    lat = models.DecimalField(decimal_places=26,max_digits=30)
    lon = models.DecimalField(decimal_places=26,max_digits=30)
    address = models.CharField(max_length = 10000,null=True,blank=True)
    QUANTIZE_EXPONENT = Decimal("0.000001")

    def init(self):
        self.tracepoints = []
        self.tracepoints_id = {}
        
    def getdistance(self,point):

        lon1, lat1, lon2, lat2 = map(math.radians , [self.lon, self.lat, point.lon, point.lat])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        km = 6367 * c
        return km
    
    def asquantizedtuple(self):
        return (Decimal(self.lat).quantize(self.QUANTIZE_EXPONENT),
                Decimal(self.lon).quantize(self.QUANTIZE_EXPONENT))
 

    def getlabel(self):
        return "%s,%s" % (self.lat,self.lon)
        
    def __unicode__(self):
        if self.address:
            return self.address
        else:
            return "%f,%f" % (self.lat,self.lon)
   
    class Meta(Point.Meta):
        pass

class TracePoint(Point):
    videotimestart = models.IntegerField()
    videotimeend = models.IntegerField()
    realtimestart = models.DateTimeField()
    realtimeend = models.DateTimeField()
    video = models.ForeignKey(Video,on_delete = models.CASCADE)
    mappoint = models.ForeignKey(MapPoint,on_delete = models.CASCADE)
    
    def __unicode__(self):
        return "%s TRACE" % self.mappoint.address

#===============================================================================
# dto
#===============================================================================

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
