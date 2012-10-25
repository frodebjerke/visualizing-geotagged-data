'''
Created on Mar 22, 2012

@author: fredo
'''

from point import Point
from django.db import models
from geo.map.point import Point
from geo.map.mappoint import MapPoint
from geo.model.video import Video

class TracePoint(Point):
    videotimestart = models.IntegerField()
    videotimeend = models.IntegerField()
    realtimestart = models.DateTimeField()
    realtimeend = models.DateTimeField()
    video = models.ForeignKey(Video,on_delete = models.CASCADE)
    mappoint = models.ForeignKey(MapPoint,on_delete = models.CASCADE)
    
    def __unicode__(self):
        return "%s TRACE" % self.mappoint.address