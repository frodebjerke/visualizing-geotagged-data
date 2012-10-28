'''
Created on Oct 28, 2012

@author: fredo
'''


from django.db import models
from geo.models import Video
from points import MapPoint,TracePoint
    

#===============================================================================
# abstract super class
#===============================================================================

class PointConnection(models.Model):
    TO_SELF_COST = 5
    TP_COST = 1
    MP_COST = 20
    mapsource = models.ForeignKey(MapPoint, related_name="%(app_label)s_%(class)s_mapsource_related", on_delete=models.CASCADE)
    maptarget = models.ForeignKey(MapPoint, related_name="%(app_label)s_%(class)s_maptarget_related", on_delete=models.CASCADE)
    cost = models.IntegerField()

    def __unicode__(self):
        return "%d -> %d" % (self.mapsource.id, self.maptarget.id)

    class Meta:
        app_label = "geo"
        abstract = True

#===============================================================================
# implementations
#===============================================================================

class TracePointConnection(PointConnection):
    
    tracesource = models.ForeignKey(TracePoint,related_name="%(app_label)s_%(class)s_tracesource_related)",on_delete = models.CASCADE)
    tracetarget = models.ForeignKey(TracePoint,related_name="%(app_label)s_%(class)s_tracetarget_related",on_delete = models.CASCADE)
    mode = models.IntegerField()
    video = models.ForeignKey(Video,related_name="+",on_delete=models.CASCADE)

class MapPointConnection(PointConnection):
    
    pass
    