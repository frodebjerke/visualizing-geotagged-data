'''
Created on Mar 23, 2012

@author: fredo
'''
from django.contrib import admin

from geo import map
from geo import model

admin.site.register(map.mappoint.MapPoint)
admin.site.register(map.mappointconnection.MapPointConnection)
admin.site.register(map.tracepoint.TracePoint)
admin.site.register(map.tracepointconnection.TracePointConnection)
admin.site.register(model.video.Video)