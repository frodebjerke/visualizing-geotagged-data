'''
Created on Mar 30, 2012

@author: fredo
'''


from geo.routing.connections import TracePointConnection
import json
import os
from django.conf import settings
import logging

class JSONX():

    logger = logging.getLogger(__name__)
    
    def __init__(self, file=None):
        "Use file if you want to read from file."
        self.file = file
    

    def pointtraces(self, pointtraces):
        data = []
        for pointtrack in pointtraces:
            pair = []
            for mappoint in pointtrack:
                pair.append({"lat" : str(mappoint.lat),
                             "lon" : str(mappoint.lon),
                             "id" : mappoint.id})
            data.append(pair)
        self.data = data

    def setconnectiontrack(self, connectiontrack, map):
        data = []
        
        self.logger.debug("PROJECT_PATH: %s", settings.PROJECT_PATH)
        for connection in connectiontrack:
            data.append(self.objectifypoint(connection.mapsource, connection, map))
        lastconnection = connectiontrack.getlastconnection()
        if lastconnection:
            data.append(self.objectifypoint(lastconnection.maptarget, lastconnection, map))
        self.data = data

    def objectifypoint(self, point, connection, map):
        jpoint = {
               "lat" : str(point.lat),
                "lon" : str(point.lon),
                "id" : str(point.id)}

        if isinstance(connection, TracePointConnection):

            tracepoint = map.gettracepoint(video=connection.video , point=point)

            jpoint["videotimestart"] = tracepoint.videotimestart
            jpoint["videotimeend"] = tracepoint.videotimeend
            jpoint["src"] = os.path.relpath(tracepoint.video.video.path, settings.PROJECT_PATH)
        return jpoint

    def getjson(self):
        print json
        return json.dumps(self.data, indent=4)

