'''
Created on Mar 23, 2012

@author: fredo
'''



from django.test.testcases import TransactionTestCase
from geo.routing.graph import Graph

from geo.io.gpx import GPX

from django.conf import settings

import os

from geo.routing.points import TracePointDTO
from decimal import Decimal

from datetime import datetime,timedelta
import logging
from StringIO import StringIO

from geo.models import createvideo

NOW = datetime.now()

def createtime(**kwargs):
    return NOW-timedelta(**kwargs)

TRACES = [
          [(Decimal(1.0),Decimal(0.5),createtime(minutes = 20),0),
           (Decimal(1.001),Decimal(0.5),createtime(minutes = 19),60),
           (Decimal(1.002),Decimal(0.5),createtime(minutes = 18),120)],
          
          [(Decimal(1.002),Decimal(0.5),createtime(minutes = 13),0),
           (Decimal(1.002),Decimal(0.501),createtime(minutes = 12),60),
           (Decimal(1.002),Decimal(0.502),createtime(minutes = 11), 120)],
          
          [(Decimal(1.002),Decimal(0.502),createtime(minutes = 6),0),
           (Decimal(1.003),Decimal(0.502),createtime(minutes = 5),60),
           (Decimal(1.004),Decimal(0.502),createtime(minutes = 4),120)]
          ]

DTO_TRACES = []
VIDEO_PATH = os.path.join(settings.TEST_PATH, "video.3gp")

#video = createvideo(VIDEO_PATH)
video = None

for trace in TRACES:
    dtos = []
    for point in trace:
        dtos.append(TracePointDTO(lat = point[0],lon = point[1], realtime = point[2],videotime = point[3],video = video))
    DTO_TRACES.append(dtos)
    
    
class GraphTest(TransactionTestCase):

    logger = logging.getLogger(__name__)

    
    
    
    TEST = 0

    def setUp(self):
        video = createvideo(VIDEO_PATH)
        self.video = video
        for trace in DTO_TRACES:
            for dto in trace:
                dto.video = video


    def testinsertmappoint1(self):
        "add points and check if they persist and the connection to themself is created"
        graph = Graph(2)
        for (lat, lon, realtime,videotime) in TRACES[0]:
            mappoint1 = graph.insertmappoint(lat, lon)
            mappoint2 = graph.getmappoint(pointid=mappoint1.id)
            mappoint3 = graph.getmappoint(lat=mappoint1.lat, lon=mappoint1.lon)

            self.assertEqual(mappoint1, mappoint2, "insert and get should retrieve the same point")
            self.assertEqual(mappoint2, mappoint3, "get with id and get with lat|lon should retrieve the same point")

            self.assertEqual(mappoint1, graph.insertmappoint(lat, lon), "a mappoint should not be created twice")



    def testinserttracepoint(self):
        oldmappoint = None
        graph = Graph(2)

        for dto in DTO_TRACES[0]:
            
            tracepoint = graph.inserttracepoint(dto)


            mappoint = graph.getmappoint(lat=dto.lat, lon=dto.lon)
            self.assertTrue(mappoint, "inserttracepoint should have created a new mappoint")

            self.assertEqual(graph.gettracepoint(video=self.video, point=mappoint), tracepoint)
            self.assertEqual(len([tracepoint for tracepoint in mappoint.tracepoints
                              if tracepoint.video == self.video]), 1, "mappoint should have exactly one tracepoint for this video")
            print "Storing Tracepoint %d in Mappoint %d " % (tracepoint.id, mappoint.id)
            if oldmappoint != None and oldmappoint == mappoint:
                self.assertEqual(tracepoint.realtimeend, dto.realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimeend, dto.videotime, "tracepoint should have video end time equalt to that one")
            else:
                self.assertEqual(tracepoint.realtimestart, dto.realtime, "tracepoint should have starting time equal to that one")
                self.assertEqual(tracepoint.realtimeend, dto.realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimeend, dto.videotime, "tracepoint should have video end time equalt to that one")
                self.assertEqual(tracepoint.videotimestart, dto.videotime, "tracepoint should have video start time equal to that one")

            oldmappoint = mappoint



    def testreverseinserttracepoint(self):
        oldmappoint = None
        
        graph = Graph(2)
        trace = DTO_TRACES[0]
        trace.reverse()
        for dto in trace:
        
            tracepoint = graph.inserttracepoint(dto)


            mappoint = graph.getmappoint(lat=dto.lat, lon=dto.lon)
            self.assertTrue(mappoint, "inserttracepoint should have created a new mappoint")

            self.assertEqual(graph.gettracepoint(video=self.video, point=mappoint), tracepoint)
            self.assertEqual(len([tracepoint for tracepoint in mappoint.tracepoints
                              if tracepoint.video == self.video]), 1, "mappoint should have exactly one tracepoint for this video")
            print "Storing Tracepoint %d in Mappoint %d " % (tracepoint.id, mappoint.id)
            if oldmappoint != None and oldmappoint == mappoint:
                self.assertEqual(tracepoint.realtimestart, dto.realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimestart, dto.videotime, "tracepoint should have video end time equalt to that one")
            else:
                self.assertEqual(tracepoint.realtimestart, dto.realtime, "tracepoint should have starting time equal to that one")
                self.assertEqual(tracepoint.realtimeend, dto.realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimeend, dto.videotime, "tracepoint should have video end time equalt to that one")
                self.assertEqual(tracepoint.videotimestart, dto.videotime, "tracepoint should have video start time equal to that one")

            oldmappoint = mappoint

    def testinserttraceconnection(self):
        oldtracepoint = None
        
        graph = Graph(2)
        for dto in DTO_TRACES[0]:
        
            tracepoint = graph.inserttracepoint(dto)

            if oldtracepoint != None and oldtracepoint != tracepoint:
                graph.inserttraceconnection(oldtracepoint, tracepoint, self.video)
                traceconnection = graph.gettraceconnection(oldtracepoint.mappoint, tracepoint.mappoint, video)
                self.assertTrue(traceconnection, "traceconnection should exist")
                traceconnections = graph.gettraceconnections(oldtracepoint.mappoint, tracepoint.mappoint)
                self.assertEqual(len(traceconnections), 1, "there should be exactly one traceconnection")
            oldtracepoint = tracepoint


    def testgetpointtracks(self):
        graph = Graph(2)
        for dtos in DTO_TRACES:
            graph.inserttracepoints(dtos)
        
        
        tracks = graph.getpointtracks()
        gpx = GPX()
        gpx.setpointtracks(tracks)
        xml = StringIO(gpx.xml.toprettyxml())
        gpx = GPX(xml, notime = True)
        
        #check one point
        trackpoints = gpx.gettrackpoints()
        self.assertEqual(len(trackpoints),12)
        exdto = TRACES[1][0]
        dto = trackpoints[4]
        self.assertAlmostEqual(dto[0],exdto[0])
        self.assertAlmostEqual(dto[1],exdto[1])


    def testshortesttracksimple(self):
        graph = Graph(2)
        graph = self.insertall(graph)
       
        sourcedto = DTO_TRACES[0][0]
        targetdto = DTO_TRACES[0][-1]
        source = graph.getmappoint(sourcedto.getlat(), sourcedto.getlon())
        target = graph.getmappoint(targetdto.getlat(), targetdto.getlon())
        track = graph.getshortesttrack(source, target)
        expected = "1>(1)2>(1)3"
        self.assertEqual(expected, str(track))
        
    def insertall(self,graph):
        for trace in DTO_TRACES:
            graph.inserttracepoints(trace)
            
        return graph


    def testshortesttrackhard(self):
        graph = Graph(2)
        self.insertall(graph)
        
        sourcedto = DTO_TRACES[0][0]
        targetdto = DTO_TRACES[2][-1]
        source = graph.getmappoint(sourcedto.getlat(), sourcedto.getlon())
        target = graph.getmappoint(targetdto.getlat(), targetdto.getlon())
        graph.draw("/tmp/graph")
        connectiontrack = graph.getshortesttrack(source, target)
        print connectiontrack
#        self.assertEqual("20>(3)21>(4)23>(4)24>(4)25>(4)26>(4)27>(4)28>(4)49>(4)50>(4)51>(4)32>(4)34>(3)35>1>(1)2>(1)3>(1)4>(1)5>(1)6>(1)7>(1)8>(1)9>(1)10>(1)11>(1)12>(1)13>(1)14>(1)15>(1)16>(1)17>(1)18>(1)19",
#                         str(self.shortestpath(sourcedto, targetdto)))
#
#        sourcedto = self.pathtodtos[self.GEOCODE5_PATH][0]
#        targetdto = self.pathtodtos[self.GEOCODE3_PATH][-1]
#        self.assertEqual("21>(4)23>(4)24>(4)25>(4)26>(4)27>(4)28>(4)49>(4)50>(4)51>(4)32>(4)34>(3)35>(3)36>(3)37>(3)38>(3)39>(3)40>(3)41>(3)42>(3)43>(3)44>(3)45>(3)46>(3)47",
#                         str(self.shortestpath(sourcedto, targetdto)))
#
#
#
#        sourcedto = self.pathtodtos[self.GEOCODE3_PATH][5]
#        targetdto = self.pathtodtos[self.GEOCODE1_PATH][4]
#        self.assertEqual("23>(4)24>(4)25>(4)26>(4)27>(4)28>(4)49>(4)50>(4)51>(4)32>(4)34>(3)35>1>(1)2>(1)3>(1)4",
#                        str(self.shortestpath(sourcedto, targetdto)))
#
#    def testshortesttrackwrong(self):
#        map = self.graph
#        self.inserttracepoints()
#        sourcedto = self.pathtodtos[self.GEOCODE3_PATH][-1]
#        targetdto = self.pathtodtos[self.GEOCODE1_PATH][0]
#        connectiontracks = self.shortestpath(sourcedto, targetdto)
#        self.assertEqual(str(connectiontracks), "")
#
#
    def shortestpath(self, sourcedto, targetdto):
        map = self.graph
        source = map.getmappoint(sourcedto.getlat(), sourcedto.getlon())
        target = map.getmappoint(targetdto.getlat(), targetdto.getlon())

        connectiontrack = map.getshortesttrack(source, target)
        print connectiontrack
        pointtrack = connectiontrack.tomappointtrack()

        path = os.path.join(settings.TEST_PATH, "shortest_path_%d_%d.gpx" % (source.id, target.id))
        gpx = GPX()
        gpx.pointtrace(pointtrack)
        gpx.write(open(path, "w"))


        return connectiontrack
#
#    pathtocolor = {
#                   GEOCODE1_PATH :"#FF0000",
#                   GEOCODE2_PATH : "#2AFF38",
#                   GEOCODE3_PATH : "#AD4343",
#                   GEOCODE4_PATH : "#275C2B",
#                   GEOCODE5_PATH : "#EBB1B1",
#                   GEOCODE6_PATH : "#81D287" }
#
#    def testgeneratealltracesgeocode(self):
#        map = self.graph
#        config = {"geocode1" : [self.pathtodtos[self.GEOCODE1_PATH], {"node_color" : self.pathtocolor[self.GEOCODE1_PATH]}],
#                  "geocode3" : [self.pathtodtos[self.GEOCODE3_PATH], {"node_color" : self.pathtocolor[self.GEOCODE3_PATH]}],
#                  "geocode5" : [self.pathtodtos[self.GEOCODE5_PATH], {"node_color" : self.pathtocolor[self.GEOCODE5_PATH]}],
#                  "geocode2" : [self.pathtodtos[self.GEOCODE2_PATH], {"node_color" : self.pathtocolor[self.GEOCODE2_PATH]}],
#                  "geocode4" : [self.pathtodtos[self.GEOCODE4_PATH], {"node_color" : self.pathtocolor[self.GEOCODE4_PATH]}],
#                  "geocode6" : [self.pathtodtos[self.GEOCODE6_PATH], {"node_color" : self.pathtocolor[self.GEOCODE6_PATH]}]
#                  }
#        path = os.path.join(settings.TEST_PATH, "all_geocode")
#
#        map.drawmultiple(config, path)
#
#    def testgeneratealltraces(self):
#        map = self.graph
#        config = {}
#        key = 1
#        for path in self.pathtodtos.keys():
#            config[key] = [self.getdtos(path), {"node_color" : self.pathtocolor[path]}]
#            key += 1
#        path = os.path.join(settings.TEST_PATH, "all_gpx")
#
#        map.drawmultiple(config, path)
#
#
#    def getdtos(self, path):
#        (name, ext) = os.path.splitext(path)
#        gpx = GPX(open(name + ".gpx"))
#        video = createvideo(self.VIDEO_PATH)
#        dtos = []
#        for (lat, lon, time) in gpx.gettrackpoint():
#            dto = TracePointDTO(lat, lon, time, 0, video)
#            dtos.append(dto)
#        return dtos
#
#
#    def inserttracepoints(self):
#        map = self.graph
#        map.inserttracepoints(self.pathtodtos[self.GEOCODE1_PATH])
#        map.inserttracepoints(self.pathtodtos[self.GEOCODE3_PATH])
#        map.inserttracepoints(self.pathtodtos[self.GEOCODE5_PATH])

