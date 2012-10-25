'''
Created on Mar 30, 2012

@author: fredo
'''

from geo.coordinate.parser import Parser
from geo.map.tracepointconnection import TracePointConnection
from geo.map.mappointconnection import MapPointConnection
from geo.map.tracepoint import TracePoint
import json
import os
from django.conf import settings
from geo.web.logger import getLogger

class JSONX(Parser):

    def setpointtracks(self, pointtracks):
        data = []
        for pointtrack in pointtracks:
            pair = []
            for mappoint in pointtrack:
                pair.append({"lat" : str(mappoint.lat),
                             "lon" : str(mappoint.lon),
                             "id" : mappoint.id})
            data.append(pair)
        self.data = data

    def setconnectiontrack(self, connectiontrack, map):
        data = []
        logger = getLogger(__name__)
        logger.debug("PROJECT_PATH: %s", settings.PROJECT_PATH)
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

