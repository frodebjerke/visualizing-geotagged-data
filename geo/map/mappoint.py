'''
Created on Mar 22, 2012

@author: fredo
'''

from django.db import models
from point import Point
from math import radians, cos, sin, asin, sqrt

class MapPoint(Point):

    lat = models.DecimalField(decimal_places=26,max_digits=30)
    lon = models.DecimalField(decimal_places=26,max_digits=30)
    address = models.CharField(max_length = 10000,null=True,blank=True)

    def init(self):
        self.tracepoints = []
        self.tracepoints_id = {}
        
    def getdistance(self,point):

        lon1, lat1, lon2, lat2 = map(radians , [self.lon, self.lat, point.lon, point.lat])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6367 * c
        return km 

    def getlabel(self):
        return "%s,%s"%(self.lat,self.lon)
        
    def __unicode__(self):
        if self.address:
            return self.address
        else:
            return "%f,%f" % (self.lat,self.lon)
   
    class Meta(Point.Meta):
        pass
