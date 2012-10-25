'''
Created on Mar 22, 2012

@author: fredo
'''

from django.db import models
from mappoint import MapPoint

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
