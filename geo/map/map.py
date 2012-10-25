'''
Created on Mar 22, 2012

@author: fredo
'''

from tracepointconnection import TracePointConnection
from mappointconnection import MapPointConnection
from pointconnection import PointConnection
from connectionmode import ConnectionMode
from exceptions import RuntimeError
from tracepointdto import TracePointDTO
from tracepoint import TracePoint
from mappoint import MapPoint
from django.db import models
from geo.map.exception import InsertTracePointException
from decimal import Decimal
import heapq
import networkx as nx
import heapq
from copy import deepcopy
from maptrack import MapConnectionTrack, MapPointTrack
from django.core.exceptions import ObjectDoesNotExist



"""Datastructure that hold Points and PointConnection"""
class Map:

    MODE_TO_MAP = {}

    MAX_DISTANCE = {
                    ConnectionMode.BIKE : 0.1,
                    ConnectionMode.MOTOR_VEHICLE : 0.5,
                    ConnectionMode.TRAIN:1,
                    ConnectionMode.WALK: 0.05}

    NODE_COLOR = "#E9D5C1"
    TRACE_EDGE_COLOR = "#FFDDDD"
    MAP_EDGE_COLOR = "#99FF99"

    def __init__(self, mode):
                #dict on id of database nodes
        self.mappoints_id = {}

        #dict on lat long [lat][lon]
        self.mappoints_latlon = {}

        #list for for loops hold all connections
        self.mappoints = []

        #all connections for loops
        self.connections = []

        #holds traceconnection as well as mapconnections
        self.mapconnections = []
        self.traceconnections = []

        #fast access with id from mapsource
        self.mapconnections_id = {}
        self.mapconnections_target_id = {}
        self.traceconnections_id = {}
        self.traceconnections_target_id = {}

        mode = int(mode)
        self.setmode(mode)
        self.maxdistance = Map.MAX_DISTANCE[mode]

        self.graph = nx.DiGraph()

        Map.setinstance(self, mode)

    @classmethod
    def getinstance(cls, mode):
#        map = None
#        try:
#            map = cls.MODE_TO_MAP[mode]
#        except KeyError:
#            map = Map.createmap(mode)
#            cls.MODE_TO_MAP[mode] = map
#        return map
        return Map.createmap(mode)

    @classmethod
    def createmap(cls, mode):

        map = Map(mode)
        traceconnections = TracePointConnection.objects.filter(mode=mode)
        #find all tracepoints that are interconnected by a tracepointconnection
        tracepoints = set()
        for connection in traceconnections:
            tracepoints.add(connection.tracesource)
            tracepoints.add(connection.tracetarget)

        #find all mappoints that are interconnected by at least on tracepointconnection with the mode
        mappoints = set()
        for tracepoint in tracepoints:
            mappoints.add(tracepoint.mappoint)

        #find all mapconnections that have source and target in the current set of mappoints
        mapconnectionsall = MapPointConnection.objects.all()
        mapconnections = set()

        for connection in mapconnectionsall:
            if connection.maptarget in mappoints and connection.mapsource in mappoints:
                mapconnections.add(connection)


        for mappoint in mappoints:
            map.addmappoint(mappoint)
        for connection in mapconnections:
            map.addmapconnection(connection)
        for tracepoint in tracepoints:
            map.addtracepoint(tracepoint)
        for connection in traceconnections:
            map.addtraceconnection(connection)

        return map

    @classmethod
    def setinstance(cls, map, mode):
        cls.MODE_TO_MAP[mode] = map

    ##########################################################
    #                MapPoint                                #
    ##########################################################

    def insertmappoint(self, lat, lon, address=None):
        "Adds the point to the map if it does not exist yet and creates a connection to the point itself. Returns the new point"
        point = self.getmappoint(lat, lon)
        if point:
            return point

        point = MapPoint(lat=lat, lon=lon, address=address)
#        point.tracepoints = []
#        point.tracepoints_id = {}

        point.save()

        self.addmappoint(point)

        return point

    def addmappoint(self, point):
        point.init()
        self.mappoints_id[point.id] = point
        self.graph.add_node(point.id)
        try:
            self.mappoints_latlon[str(point.lat)]
        except KeyError as e:
            self.mappoints_latlon[str(point.lat)] = {}

        self.mappoints_latlon[str(point.lat)][str(point.lon)] = point
        self.mappoints.append(point)


    def getmappoint(self, lat=None, lon=None, pointid=None):
        "Searches the mappoint with the fastest access possible"
        point = None
        try:
            if pointid:
                point = self.mappoints_id[pointid]
            elif lat and lon:
                point = self.mappoints_latlon[str(lat)][str(lon)]
        except KeyError as e:
            pass
        return point

    ##########################################################
    #                TracePoint                              #
    ##########################################################   


    def inserttracepoint(self, dto):
        "Adds the trace point to the map or updates the time of and existing one and creates a map point if it does not exist yet"
        mappoint = self.getmappoint(lat=dto.getlat(), lon=dto.getlon())

        #try to get mappoint from current map insert it if it does not exist

        if not mappoint:
            mappoint = self.insertmappoint(lat=dto.getlat(), lon=dto.getlon(), address=dto.getaddress())

        add = False

        tracepoint = self.gettracepoint(video=dto.getvideo(), point=mappoint)
        if not tracepoint:
            tracepoint = TracePoint(videotimestart=dto.getvideotime(),
                                    videotimeend=dto.getvideotime(),
                                    realtimestart=dto.getrealtime(),
                                    realtimeend=dto.getrealtime(),
                                    video=dto.getvideo(),
                                    mappoint=mappoint)
            add = True

        if tracepoint.videotimeend <= dto.getvideotime():
            tracepoint.videotimeend = dto.getvideotime()
            tracepoint.realtimeend = dto.getrealtime()


        if dto.getvideotime() <= tracepoint.videotimestart :
            tracepoint.videotimestart = dto.getvideotime()
            tracepoint.realtimestart = dto.getrealtime()

        tracepoint.save()

        if add:
            self.addtracepoint(tracepoint)

        return tracepoint


    def addtracepoint(self, tracepoint):

        mappoint = self.getmappoint(pointid=tracepoint.mappoint.id)
        mappoint.tracepoints_id[tracepoint.video.id] = tracepoint
        mappoint.tracepoints.append(tracepoint)

        return tracepoint

    def inserttracepoints(self, dtos):
        "add all tracepoints as dto in order of direction"
        oldtracepoint = None
        tracepoints = []
        for dto in dtos:
            tracepoint = self.inserttracepoint(dto)

            if oldtracepoint != None and oldtracepoint != tracepoint:
                self.inserttraceconnection(oldtracepoint, tracepoint, dto.getvideo())
            oldtracepoint = tracepoint
            tracepoints.append(tracepoint)
        self.__connectmappoints()

    def gettracepoint(self, video, lat=None, lon=None, point=None):

        mappoint = None
        if lat and lon:
            mappoint = self.getmappoint(lat, lon)
        elif point:
            mappoint = point
        tracepoint = None
        try:
            tracepoint = mappoint.tracepoints_id[video.id]
        except Exception:
            pass
        if not tracepoint:
            try:
                tracepoint = TracePoint.objects.get(video=video, mappoint=point)
            except ObjectDoesNotExist:
                pass

        return tracepoint

    ##########################################################
    #                TraceConnection                         #
    ##########################################################      

    def inserttraceconnection(self, tracesource, tracetarget, video):
        "Creates a new traceconnection and returns it"
        con = TracePointConnection(mapsource=tracesource.mappoint,
                                   maptarget=tracetarget.mappoint,
                                   tracesource=tracesource,
                                   tracetarget=tracetarget,
                                   video=video,
                                   cost=PointConnection.TP_COST,
                                   mode=self.mode)
        con.save()
        self.addtraceconnection(con)
        return con

    def addtraceconnection(self, con):
        return self.addconnection(con, self.traceconnections_id, self.traceconnections_target_id)

    def gettraceconnections(self, source=None, target=None):
        if source:
            return self.getconnections(self.traceconnections_id, source)
        else:
            return self.getconnections(self.traceconnections_target_id, target)

    def gettraceconnection(self, source=None, target=None, video=None):
        cons = self.gettraceconnections(source, target)
        if video:
            return [con for con in cons if con.video == video]
        else:
            return cons

    ##########################################################
    #                MapConnection                           #
    ##########################################################

    def insertmapconnection(self, source, target, cost):
        "Creates a new map connection between two non identical points and returns it"
        con = MapPointConnection(mapsource=source,
                                 maptarget=target,
                                 cost=cost)
        con.save()
        #add mapconnection
        self.addmapconnection(con)

        return con

    def addmapconnection(self, con):
        self.addconnection(con, self.mapconnections_id, self.mapconnections_target_id)


    def getmapconnections(self, source=None, target=None):
        if source:
            return self.getconnections(self.mapconnections_id, source)
        else:
            return self.getconnections(self.mapconnections_target_id, target)


    ##########################################################
    #                Utility                                 #
    ##########################################################

    def hasmapconnection(self, source, target):
        "Returns the map connection between source and target. There should only be one"
        for con in self.mapconnections_id.get(source.id, []):
            if con.maptarget == target:
                return True
            else:
                return False



    def __connectmappoints(self):
        if nx.is_connected(self.graph.to_undirected()):
            return None

        connected_components = nx.connected_components(self.graph.to_undirected())
        nearestsource = None
        nearesttarget = None
        for component in connected_components:

            othercomponents = [ocomponent for ocomponent in connected_components if component != ocomponent]

            for ocomponent in othercomponents:
                nearestsource = None
                nearesttarget = None
                nearestdistance = None

                for point in component:
                    source = self.getmappoint(pointid=point)

                    for opoint in ocomponent:
                        target = self.getmappoint(pointid=opoint)
                        distance = source.getdistance(target)
                        if nearestdistance == None or distance < nearestdistance:
                            nearesttarget = target
                            nearestsource = source
                            nearestdistance = distance


                self.insertmapconnection(nearestsource, nearesttarget, PointConnection.MP_COST)


    def drawmultiple(self, config, path):
        for key in config.keys():
            all = config[key];
            dtos = all[0]
            colors = all[1]
            try:
                node_color = colors["node_color"]
            except KeyError :
                node_color = Map.NODE_COLOR

            try:
                trace_edge_color = colors["trace_edge_color"]
            except KeyError :
                trace_edge_color = Map.TRACE_EDGE_COLOR

            try:
                map_edge_color = colors["map_edge_color"]
            except KeyError:
                map_edge_color = Map.MAP_EDGE_COLOR


            self.inserttracepoints(dtos)
            self.draw(path, node_color, trace_edge_color, map_edge_color, reset=False, draw_tracepoints=False)
            self.__init__(self.mode)



    def draw(self, path, node_color=None, trace_edge_color=None, map_edge_color=None, reset=True, draw_tracepoints=True):

        from decimal import Decimal
        import matplotlib.pyplot as plt

        if not node_color:
            node_color = Map.NODE_COLOR
        if not trace_edge_color :
            trace_edge_color = Map.TRACE_EDGE_COLOR
        if not map_edge_color :
            map_edge_color = Map.MAP_EDGE_COLOR

        mapconnectiongraph = nx.DiGraph()
        traceconnectiongraph = nx.DiGraph()
        (x0, y0) = (Decimal("49.48155") * 100, Decimal("8.45499") * 100)
        (x1, y1) = (Decimal("49.49092") * 100, Decimal("8.47102") * 100)

        pos = {}
        node_colors = []
        map_edge_colors = []
        trace_edge_colors = []

        for point in self.mappoints:
            label = point.getlabel()
            coords = [float(point.lat * 100 - x0) * 1000 , float(y1 - point.lon * 100) * 1000 ]
            pos[label] = coords
            node_colors.append(node_color)
            mapconnectiongraph.add_node(label)
            traceconnectiongraph.add_node(label)


        for connection in self.connections:

            graph = None
            color = None
            if isinstance(connection, TracePointConnection):
                trace_edge_colors.append(trace_edge_color)
                graph = traceconnectiongraph

            else:
                graph = mapconnectiongraph
                map_edge_colors.append(map_edge_color)

            graph.add_edge(connection.mapsource.getlabel(), connection.maptarget.getlabel(), cost=connection.cost)


        if reset:
            figure = plt.figure(figsize=(20, 20))
        else:
            figure = plt.gcf();
            figure.set_size_inches(20, 20)
            plt.figure(figure.number)

        nx.draw_networkx(mapconnectiongraph, pos, False, node_color=node_colors, edge_color=map_edge_colors)
        nx.draw_networkx_edge_labels(mapconnectiongraph, pos, font_size=5)

        plt.savefig(path + "_map.png")

        if draw_tracepoints :
            if reset:
                figure = plt.figure(figsize=(20, 20))

            mapconnectiongraph = None
            nx.draw_networkx(traceconnectiongraph, pos, False, node_color=node_colors)
            nx.draw_networkx_edge_labels(traceconnectiongraph, pos, font_size=5)

            plt.savefig(path + "_trace.png")

    def getallconnections(self, source=None, target=None):
        connections = []
        if source:
            connections.extend(self.gettraceconnections(source))
            connections.extend(self.getmapconnections(source))
        else :
            connections.extend(self.gettraceconnections(target=target))
            connections.extend(self.getmapconnections(target=target))

        return connections

    def initshortesttrack(self, startconnections):
        for connection in startconnections:
            connection.totalcost = connection.cost
            connection.predecessor = None
        for connection in [connection for connection in self.connections
                           if connection not in startconnections]:
            connection.totalcost = Decimal("Infinity")
            connection.predecessor = None


    def shortesttrack(self, start):
        startconnections = self.getallconnections(start)
        self.initshortesttrack(startconnections)

        oldconnections = deepcopy(self.connections)
        visitedconnections = []
        unvisitedconnections = self.connections

        while unvisitedconnections:

            minimalcost = [(connection.totalcost, connection) for connection in unvisitedconnections]
            heapq.heapify(minimalcost)

            (cost, connection) = heapq.heappop(minimalcost)
            visitedconnections.append(connection)
            unvisitedconnections.remove(connection)

            successors = self.getallconnections(connection.maptarget)

            for successor in successors:
                self.relax(connection, successor)

    def getshortesttrack(self, source, target):
        print "Starting single source shortest path from %d to %d" % (source.id, target.id)
        self.shortesttrack(source)
        print "Finshed single source shortest path"
        shortesttrack = MapConnectionTrack()
        currentconnection = None
        totalcost = None
        totarget = self.getallconnections(target=target)


        print "Searching cheapest end connection"
        for connection in totarget:
            if connection.totalcost < totalcost or totalcost == None:
                currentconnection = connection
                totalcost = connection.totalcost

        if not totarget or totalcost == Decimal("Infinity"):
            print "Did not find a connection to the target point"
            return shortesttrack

        print "Found %s with totalcost %s" % (currentconnection, str(totalcost))
        currentpoint = target
        while currentpoint != source and currentconnection != None:
            shortesttrack.addconnection(currentconnection)
            currentpoint = currentconnection.mapsource
            currentconnection = currentconnection.predecessor

        if currentpoint != source:
            shortesttrack.reset()


        shortesttrack.finish()

        return shortesttrack


    def relax(self, connection, successor):
        newcost = connection.totalcost + successor.cost

        if newcost < successor.totalcost:
            successor.predecessor = connection
            successor.totalcost = newcost
        elif newcost == successor.totalcost and hasattr(successor, "video") and hasattr(connection, "video") and successor.video == connection.video:
            successor.predecessor = connection

    def getpointtracks(self):

        if not self.connections:
            return []

        tracks = []
        visited = {}

        for connection in self.connections:

            #connection already visited
            try:
                if visited[str(connection.mapsource.id) + "," + str(connection.maptarget.id)]:
                    continue
            except KeyError:
                pass

            currenttrack = MapPointTrack()
            currenttrack.addpoint(connection.mapsource)
            currenttrack.addpoint(connection.maptarget)
            tracks.append(currenttrack)

        return tracks


    def __getpointtracks(self, point, visited, currenttrack, tracks, lasttrackppoints):
        if not lasttrackppoints["first"]:
            lasttrackppoints["first"] = point
        lasttrackppoints["last"] = point
        visited[point.id] = True
#        currenttrack.addpoint(point)

        neighbours = self.getneighbours(point)
        for neighbour in neighbours:


            currenttrack.addpoint(point)
            currenttrack.addpoint(neighbour)
            tracks.append(currenttrack)

            currenttrack = MapPointTrack()
            try:
                if visited[neighbour.id]:
                    continue
            except KeyError:
                pass
            self.__getpointtracks(neighbour, visited, currenttrack, tracks, lasttrackppoints)



    def getneighbours(self, point):
        neighbours = set([])
        for connection in self.getallconnections(source=point):
            neighbours.add(connection.maptarget)
        return neighbours

    def setmode(self, mode):
        if not mode in (ConnectionMode.WALK, ConnectionMode.TRAIN, ConnectionMode.MOTOR_VEHICLE, ConnectionMode.BIKE):
            raise RuntimeError , "Mode " + str(mode) + " should be one of ConnectionMode"
        else:
            self.mode = mode

    def addconnection(self, con, sourcecons, targetcons):
        self.connections.append(con)
        self.graph.add_edge(con.mapsource.id, con.maptarget.id)
        self.addconnectionsource(con, sourcecons)
        self.addconnectiontarget(con, targetcons)
        return con

    def addconnectionsource(self, con, cons):

        try:
            cons[con.mapsource.id]
        except KeyError as e:
            cons[con.mapsource.id] = []
        cons[con.mapsource.id].append(con)
        return con


    def addconnectiontarget(self, con, cons):
        try:
            cons[con.maptarget.id]
        except KeyError:
            cons[con.maptarget.id] = []
        cons[con.maptarget.id].append(con)
        return con

    def getconnections(self, cons, point=None):
        newcons = []


        try:
            newcons = cons[point.id]
        except KeyError:
            pass

        return newcons


