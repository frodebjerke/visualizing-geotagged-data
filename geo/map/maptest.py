'''
Created on Mar 23, 2012

@author: fredo
'''



from django.test.testcases import TransactionTestCase
from geo.map.map import Map
from geo.coordinate.gpxtest import GPXTest
from geo.coordinate.gpx import GPX
from geo.osm import OSM
from django.conf import settings
from geo.script.gpxtogeocode import filetodto
from django.db import transaction
import os
import pickle
from geo.map.tracepointdto import TracePointDTO
from geo.coordinate.gpx import GPX

from geo.model.videofactory import VideoFactory

class MapTest(TransactionTestCase):



    GEOCODE1_PATH = os.path.join(settings.TEST_PATH, "full1.geocode")
    GEOCODE2_PATH = os.path.join(settings.TEST_PATH, "full2.geocode")
    GEOCODE3_PATH = os.path.join(settings.TEST_PATH, "full3.geocode")
    GEOCODE4_PATH = os.path.join(settings.TEST_PATH, "full4.geocode")
    GEOCODE5_PATH = os.path.join(settings.TEST_PATH, "full5.geocode")
    GEOCODE6_PATH = os.path.join(settings.TEST_PATH, "full6.geocode")
    VIDEO_PATH = os.path.join(settings.TEST_PATH, "video.3gp")
    TEST = 0

    def setUp(self):
        self.map = Map(2)
        self.gpx = GPX(GPXTest.VALID_PATH)
        self.osm = OSM()
        self.geocodes1 = pickle.load(open(self.GEOCODE1_PATH))
        self.geocodes2 = pickle.load(open(self.GEOCODE2_PATH))
        self.geocodes3 = pickle.load(open(self.GEOCODE3_PATH))
        self.geocodes5 = pickle.load(open(self.GEOCODE5_PATH))
        pathtodtos = {self.GEOCODE1_PATH : [],
                      self.GEOCODE2_PATH : [],
                      self.GEOCODE3_PATH : [],
                      self.GEOCODE4_PATH : [],
                      self.GEOCODE5_PATH : [],
                      self.GEOCODE6_PATH : []
                        }

        keys = pathtodtos.keys()
        keys.sort()
        for path in keys:
            pathtodtos[path] = filetodto(path, self.VIDEO_PATH)
        self.pathtodtos = pathtodtos

    def tearDown(self):
        self.map.draw(os.path.join(settings.TEST_PATH, str(MapTest.TEST)))
        MapTest.TEST += 1


    def testinsertmappoint1(self):
        "add points and check if they persist and the connection to themself is created"
        map = self.map
        for (lat, lon, address, realtime, videotime) in self.geocodes1:
            mappoint1 = map.insertmappoint(lat, lon, address)
            mappoint2 = map.getmappoint(pointid=mappoint1.id)
            mappoint3 = map.getmappoint(lat=mappoint1.lat, lon=mappoint1.lon)

            self.assertEqual(mappoint1, mappoint2, "insert and get should retrieve the same point")
            self.assertEqual(mappoint2, mappoint3, "get with id and get with lat|lon should retrieve the same point")

            self.assertEqual(mappoint1, map.insertmappoint(lat, lon, address), "a mappoint should not be created twice")



    def testinserttracepoint(self):
        oldmappoint = None
        video = VideoFactory.createvideo(self.VIDEO_PATH)
        map = self.map

        for (lat, lon, address, realtime, videotime) in self.geocodes1:
            dto = TracePointDTO(lat=lat, lon=lon, realtime=realtime, videotime=videotime, video=video, address=address)
            tracepoint = map.inserttracepoint(dto)


            mappoint = map.getmappoint(lat=lat, lon=lon)
            self.assertTrue(mappoint, "inserttracepoint should have created a new mappoint")

            self.assertEqual(map.gettracepoint(video=video, point=mappoint), tracepoint)
            self.assertEqual(len([tracepoint for tracepoint in mappoint.tracepoints
                              if tracepoint.video == video]), 1, "mappoint should have exactly one tracepoint for this video")
            print "Storing Tracepoint %d in Mappoint %d " % (tracepoint.id, mappoint.id)
            if oldmappoint != None and oldmappoint == mappoint:
                self.assertEqual(tracepoint.realtimeend, realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimeend, videotime, "tracepoint should have video end time equalt to that one")
            else:
                self.assertEqual(tracepoint.realtimestart, realtime, "tracepoint should have starting time equal to that one")
                self.assertEqual(tracepoint.realtimeend, realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimeend, videotime, "tracepoint should have video end time equalt to that one")
                self.assertEqual(tracepoint.videotimestart, videotime, "tracepoint should have video start time equal to that one")

            oldmappoint = mappoint



    def testreverseinserttracepoint(self):
        oldmappoint = None
        video = VideoFactory.createvideo(self.VIDEO_PATH)
        map = self.map
        self.geocodes1.reverse()
        for (lat, lon, address, realtime, videotime) in self.geocodes1:
            dto = TracePointDTO(lat=lat, lon=lon, realtime=realtime, videotime=videotime, video=video, address=address)
            tracepoint = map.inserttracepoint(dto)


            mappoint = map.getmappoint(lat=lat, lon=lon)
            self.assertTrue(mappoint, "inserttracepoint should have created a new mappoint")

            self.assertEqual(map.gettracepoint(video=video, point=mappoint), tracepoint)
            self.assertEqual(len([tracepoint for tracepoint in mappoint.tracepoints
                              if tracepoint.video == video]), 1, "mappoint should have exactly one tracepoint for this video")
            print "Storing Tracepoint %d in Mappoint %d " % (tracepoint.id, mappoint.id)
            if oldmappoint != None and oldmappoint == mappoint:
                self.assertEqual(tracepoint.realtimestart, realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimestart, videotime, "tracepoint should have video end time equalt to that one")
            else:
                self.assertEqual(tracepoint.realtimestart, realtime, "tracepoint should have starting time equal to that one")
                self.assertEqual(tracepoint.realtimeend, realtime, "tracepoint should have ending time equal to that one")
                self.assertEqual(tracepoint.videotimeend, videotime, "tracepoint should have video end time equalt to that one")
                self.assertEqual(tracepoint.videotimestart, videotime, "tracepoint should have video start time equal to that one")

            oldmappoint = mappoint

    def testinserttraceconnection(self):
        oldtracepoint = None
        video = VideoFactory.createvideo(self.VIDEO_PATH)
        map = self.map
        for (lat, lon, address, realtime, videotime) in self.geocodes1:
            dto = TracePointDTO(lat=lat, lon=lon, realtime=realtime, videotime=videotime, video=video, address=address)
            tracepoint = map.inserttracepoint(dto)

            if oldtracepoint != None and oldtracepoint != tracepoint:
                map.inserttraceconnection(oldtracepoint, tracepoint, video)
                traceconnection = map.gettraceconnection(oldtracepoint.mappoint, tracepoint.mappoint, video)
                self.assertTrue(traceconnection, "traceconnection should exist")
                traceconnections = map.gettraceconnections(oldtracepoint.mappoint, tracepoint.mappoint)
                self.assertEqual(len(traceconnections), 1, "there should be exactly one traceconnection")
            oldtracepoint = tracepoint


    def testgetpointtracks(self):
        from geo.coordinate.gpx import GPX
        map = self.map
        map.inserttracepoints(self.pathtodtos[self.GEOCODE1_PATH])
        tracks = map.getpointtracks()
        path = os.path.join(settings.TEST_PATH, "all1.gpx")
        gpx = GPX()
        gpx.setpointtracks(tracks)
        gpx.write(open(path, "w"))
        map.inserttracepoints(self.pathtodtos[self.GEOCODE3_PATH])
        tracks = map.getpointtracks()
        path = os.path.join(settings.TEST_PATH, "all2.gpx")
        gpx = GPX()
        gpx.setpointtracks(tracks)
        gpx.write(open(path, "w"))
        map.inserttracepoints(self.pathtodtos[self.GEOCODE5_PATH])
        tracks = map.getpointtracks()
        path = os.path.join(settings.TEST_PATH, "all3.gpx")
        gpx = GPX()
        gpx.setpointtracks(tracks)
        gpx.write(open(path, "w"))

        expected = open(os.path.join(settings.TEST_PATH, "all3.gpx"), "r").read()
        got = open(os.path.join(settings.TEST_PATH, "all1_3_5.gpx"), "r").read()

        self.assertEqual(expected, got, "should be equal to file content")




#        expected = open(os.path.join(settings.TEST_PATH, "full1_all.gpx"), "r").read()
#        got = open(path, "r").read()
#        self.assertEqual(expected, got)

    def testshortesttracksimple(self):
        map = self.map
        map.inserttracepoints(self.pathtodtos[self.GEOCODE1_PATH])
        sourcedto = self.pathtodtos[self.GEOCODE1_PATH][0]
        targetdto = self.pathtodtos[self.GEOCODE1_PATH][-1]
        source = self.map.getmappoint(sourcedto.getlat(), sourcedto.getlon())
        target = self.map.getmappoint(targetdto.getlat(), targetdto.getlon())
        track = map.getshortesttrack(source, target)
        expected = "1>(1)2>(1)3>(1)4>(1)5>(1)6>(1)7>(1)8>(1)9>(1)10>(1)11>(1)12>(1)13>(1)14>(1)15>(1)16>(1)17>(1)18>(1)19"
        self.assertEqual(expected, str(track))

    def testshortesttrackhard(self):
        map = self.map
        self.inserttracepoints()
        sourcedto = self.pathtodtos[self.GEOCODE3_PATH][0]
        targetdto = self.pathtodtos[self.GEOCODE1_PATH][-1]
        self.assertEqual("20>(3)21>(4)23>(4)24>(4)25>(4)26>(4)27>(4)28>(4)49>(4)50>(4)51>(4)32>(4)34>(3)35>1>(1)2>(1)3>(1)4>(1)5>(1)6>(1)7>(1)8>(1)9>(1)10>(1)11>(1)12>(1)13>(1)14>(1)15>(1)16>(1)17>(1)18>(1)19",
                         str(self.shortestpath(sourcedto, targetdto)))

        sourcedto = self.pathtodtos[self.GEOCODE5_PATH][0]
        targetdto = self.pathtodtos[self.GEOCODE3_PATH][-1]
        self.assertEqual("21>(4)23>(4)24>(4)25>(4)26>(4)27>(4)28>(4)49>(4)50>(4)51>(4)32>(4)34>(3)35>(3)36>(3)37>(3)38>(3)39>(3)40>(3)41>(3)42>(3)43>(3)44>(3)45>(3)46>(3)47",
                         str(self.shortestpath(sourcedto, targetdto)))



        sourcedto = self.pathtodtos[self.GEOCODE3_PATH][5]
        targetdto = self.pathtodtos[self.GEOCODE1_PATH][4]
        self.assertEqual("23>(4)24>(4)25>(4)26>(4)27>(4)28>(4)49>(4)50>(4)51>(4)32>(4)34>(3)35>1>(1)2>(1)3>(1)4",
                        str(self.shortestpath(sourcedto, targetdto)))

    def testshortesttrackwrong(self):
        map = self.map
        self.inserttracepoints()
        sourcedto = self.pathtodtos[self.GEOCODE3_PATH][-1]
        targetdto = self.pathtodtos[self.GEOCODE1_PATH][0]
        connectiontracks = self.shortestpath(sourcedto, targetdto)
        self.assertEqual(str(connectiontracks), "")


    def shortestpath(self, sourcedto, targetdto):
        map = self.map
        source = map.getmappoint(sourcedto.getlat(), sourcedto.getlon())
        target = map.getmappoint(targetdto.getlat(), targetdto.getlon())

        connectiontrack = map.getshortesttrack(source, target)
        print connectiontrack
        pointtrack = connectiontrack.tomappointtrack()

        path = os.path.join(settings.TEST_PATH, "shortest_path_%d_%d.gpx" % (source.id, target.id))
        gpx = GPX()
        gpx.setpointtrack(pointtrack)
        gpx.write(open(path, "w"))


        return connectiontrack

    pathtocolor = {
                   GEOCODE1_PATH :"#FF0000",
                   GEOCODE2_PATH : "#2AFF38",
                   GEOCODE3_PATH : "#AD4343",
                   GEOCODE4_PATH : "#275C2B",
                   GEOCODE5_PATH : "#EBB1B1",
                   GEOCODE6_PATH : "#81D287" }

    def testgeneratealltracesgeocode(self):
        map = self.map
        config = {"geocode1" : [self.pathtodtos[self.GEOCODE1_PATH], {"node_color" : self.pathtocolor[self.GEOCODE1_PATH]}],
                  "geocode3" : [self.pathtodtos[self.GEOCODE3_PATH], {"node_color" : self.pathtocolor[self.GEOCODE3_PATH]}],
                  "geocode5" : [self.pathtodtos[self.GEOCODE5_PATH], {"node_color" : self.pathtocolor[self.GEOCODE5_PATH]}],
                  "geocode2" : [self.pathtodtos[self.GEOCODE2_PATH], {"node_color" : self.pathtocolor[self.GEOCODE2_PATH]}],
                  "geocode4" : [self.pathtodtos[self.GEOCODE4_PATH], {"node_color" : self.pathtocolor[self.GEOCODE4_PATH]}],
                  "geocode6" : [self.pathtodtos[self.GEOCODE6_PATH], {"node_color" : self.pathtocolor[self.GEOCODE6_PATH]}]
                  }
        path = os.path.join(settings.TEST_PATH, "all_geocode")

        map.drawmultiple(config, path)

    def testgeneratealltraces(self):
        map = self.map
        config = {}
        key = 1
        for path in self.pathtodtos.keys():
            config[key] = [self.getdtos(path), {"node_color" : self.pathtocolor[path]}]
            key += 1
        path = os.path.join(settings.TEST_PATH, "all_gpx")

        map.drawmultiple(config, path)


    def getdtos(self, path):
        (name, ext) = os.path.splitext(path)
        gpx = GPX(open(name + ".gpx"))
        video = VideoFactory.createvideo(self.VIDEO_PATH)
        dtos = []
        for (lat, lon, time) in gpx.gettrackpoint():
            dto = TracePointDTO(lat, lon, time, 0, video)
            dtos.append(dto)
        return dtos


    def inserttracepoints(self):
        map = self.map
        map.inserttracepoints(self.pathtodtos[self.GEOCODE1_PATH])
        map.inserttracepoints(self.pathtodtos[self.GEOCODE3_PATH])
        map.inserttracepoints(self.pathtodtos[self.GEOCODE5_PATH])

