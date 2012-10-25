'''
Created on Mar 22, 2012

@author: fredo
'''

from django.db import models
from pointconnection import PointConnection
from tracepoint import TracePoint
from geo.model.video import Video
from django.conf import settings



class TracePointConnection(PointConnection):
    
    tracesource = models.ForeignKey(TracePoint,related_name="%(app_label)s_%(class)s_tracesource_related)",on_delete = models.CASCADE)
    tracetarget = models.ForeignKey(TracePoint,related_name="%(app_label)s_%(class)s_tracetarget_related",on_delete = models.CASCADE)
    mode = models.IntegerField()
    video = models.ForeignKey(Video,related_name="+",on_delete=models.CASCADE)
    
    