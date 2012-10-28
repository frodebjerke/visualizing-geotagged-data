'''
Created on Mar 23, 2012

@author: fredo
'''
from django.contrib import admin

from geo import routing
from geo import models

admin.site.register(routing.points.MapPoint)
admin.site.register(routing.connections.MapPointConnection)
admin.site.register(routing.points.TracePoint)
admin.site.register(routing.connections.TracePointConnection)
admin.site.register(models.Video)