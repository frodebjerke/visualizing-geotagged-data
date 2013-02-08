'''
Created on Mar 22, 2012

@author: fredo
'''

from connections import PointConnection,TracePointConnection,MapPointConnection
from exceptions import RuntimeError
from points import TracePoint,MapPoint
from decimal import Decimal
import networkx as nx
import heapq
from copy import copy
from util import MapConnectionTrace, MapPointTrace, ConnectionMode
from django.core.exceptions import ObjectDoesNotExist
import logging

import matplotlib.pyplot as plt

"""Datastructure that hold Points and PointConnection"""
class Graph:

    MODE_TO_MAP = {}

    MAX_DISTANCE = {
                    ConnectionMode.BIKE : 0.1,
                    ConnectionMode.MOTOR_VEHICLE : 0.5,
                    ConnectionMode.TRAIN:1,
                    ConnectionMode.WALK: 0.05}

    NODE_COLOR = "#E9D5C1"
    TRACE_EDGE_COLOR = "#FFDDDD"
    MAP_EDGE_COLOR = "#99FF99"
    
    logger = logging.getLogger(__name__)

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
#        self.mapconnections = []
#        self.traceconnections = []

        #fast access with id from mapsource
        self.mapconnections_id = {}
        self.mapconnections_target_id = {}
        self.traceconnections_id = {}
        self.traceconnections_target_id = {}

        mode = int(mode)
        self.setmode(mode)
        self.maxdistance = self.MAX_DISTANCE[mode]

        self.graph = nx.DiGraph()

        self.setinstance(self, mode)

    @classmethod
    def getinstance(cls, mode):
#        map = None
#        try:
#            map = cls.MODE_TO_MAP[mode]
#        except KeyError:
#            map = Graph.createmap(mode)
#            cls.MODE_TO_MAP[mode] = map
#        return map
        return Graph.createmap(mode)

    @classmethod
    def createmap(cls, mode):

        graph = Graph(mode)
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
            graph.addmappoint(mappoint)
        for connection in mapconnections:
            graph.addmapconnection(connection)
        for tracepoint in tracepoints:
            graph.addtracepoint(tracepoint)
        for connection in traceconnections:
            graph.addtraceconnection(connection)

        return graph

    @classmethod
    def setinstance(cls, map, mode):
        cls.MODE_TO_MAP[mode] = map

    ##########################################################
    #                MapPoint                                #
    ##########################################################

    def insertmappoint(self, lat, lon, address=None):
        "Adds the point to the map if it does not exist yet and creates a connection to the point itself. Returns the new point"
        self.logger.debug("Adding %s,%s as mappoint." % (lat,lon))
        point = MapPoint(lat=lat, lon=lon, address=address)

        point.save()
        self.addmappoint(point)

        return point

    def addmappoint(self, point):
        self.mappoints_id[point.id] = point
        self.graph.add_node(point.id)
        try:
            self.mappoints_latlon[str(point.lat)]
        except KeyError as e:
            self.mappoints_latlon[str(point.lat)] = {}
        
        assert not self.mappoints_latlon[str(point.lat)].has_key(str(point.lon))
        self.mappoints_latlon[str(point.lat)][str(point.lon)] = point
        self.mappoints.append(point)


    def getmappoint(self, lat=None, lon=None, pointid=None):
        '''
        @summary Searches the mappoint with the fastest access possible
        @note This caching works fine, because Graph is not a model and manages every other instance
                @see gettracepoint
        '''
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
            self.logger.debug("Adding %s,%s as tracepoint." % (dto.getlat(), dto.getlon()))
            tracepoint = TracePoint(videotimestart=dto.getvideotime(),
                                    videotimeend=dto.getvideotime(),
                                    realtimestart=dto.getrealtime(),
                                    realtimeend=dto.getrealtime(),
                                    video=dto.getvideo(),
                                    mappoint=mappoint)
            add = True
        else:
            self.logger.debug("Updating tracepoint %s." % tracepoint)

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
        """ This way of caching does not work @see gettracepoint for details """
#        mappoint.tracepoints_id[tracepoint.video.id] = tracepoint
#        mappoint.tracepoints.append(tracepoint)

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
        '''
        @note Caching of instances does not work well with django orm.
                This is because TracePoint and MapPoint are referenced by other models.
                Now, because you need to query each individually, you create several instances of 
                the same record. This will lead you into trouble when you attach some attributes to 
                one of this instances and try to access it via another model instance. The instance
                will still hold the old state without the new attribute. This makes for really confusing
                and hard to discover errors.
        ''' 
        mappoint = None
        if lat and lon:
            mappoint = self.getmappoint(lat, lon)
        elif point:
            mappoint = point
        tracepoint = None
        try:
            #get the correct tracepoint from the db
            tracepoint = TracePoint.objects.get(mappoint = mappoint, video = video)
        except Exception:
            pass
#        if not tracepoint:
#            try:
#                tracepoint = TracePoint.objects.get(video=video, mappoint=point)
#            except ObjectDoesNotExist:
#                pass

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
                node_color = self.NODE_COLOR

            try:
                trace_edge_color = colors["trace_edge_color"]
            except KeyError :
                trace_edge_color = self.TRACE_EDGE_COLOR

            try:
                map_edge_color = colors["map_edge_color"]
            except KeyError:
                map_edge_color = self.MAP_EDGE_COLOR


            self.inserttracepoints(dtos)
            self.draw(path, node_color, trace_edge_color, map_edge_color, reset=False, draw_tracepoints=False)
            self.__init__(self.mode)



    def draw(self, path, node_color=None, trace_edge_color=None, map_edge_color=None, reset=True, draw_tracepoints=True):

        

        if not node_color:
            node_color = self.NODE_COLOR
        if not trace_edge_color :
            trace_edge_color = self.TRACE_EDGE_COLOR
        if not map_edge_color :
            map_edge_color = self.MAP_EDGE_COLOR

        mapconnectiongraph = nx.DiGraph()
        traceconnectiongraph = nx.DiGraph()
#        (x0, y0) = (Decimal("49.48155") * 100, Decimal("8.45499") * 100)
#        (x1, y1) = (Decimal("49.49092") * 100, Decimal("8.47102") * 100)

        pos = {}
        node_colors = []
        map_edge_colors = []
        trace_edge_colors = []
        edge_colors = []
        
        (commonplaceslat, commonplaceslon) = self.getcommondecimalplaces()

        for point in self.mappoints:
            name = point.getlabel()
            coord = self._cutdecimalplaces(point, commonplaceslat, commonplaceslon)
            pos[name] = [float(x) for x in coord]
            node_colors.append(node_color)
            mapconnectiongraph.add_node(name)
            traceconnectiongraph.add_node(name)


        for connection in self.connections:

            graph = None
            color = None
            if isinstance(connection, TracePointConnection):
                trace_edge_colors.append(trace_edge_color)
                graph = traceconnectiongraph
                edge_colors.append(trace_edge_color)

            else:
                graph = mapconnectiongraph
                map_edge_colors.append(map_edge_color)
                edge_colors.append(map_edge_color)

            graph.add_edge(connection.mapsource.getlabel(), connection.maptarget.getlabel(), cost=connection.cost)


        if reset:
            figure = plt.figure(figsize=(20, 20))
        else:
            figure = plt.gcf();
            figure.set_size_inches(20, 20)
            plt.figure(figure.number)

        nx.draw_networkx(mapconnectiongraph, pos, False, node_color=node_colors, edge_color=map_edge_color)
        nx.draw_networkx_edge_labels(mapconnectiongraph, pos, font_size=5)

        plt.savefig(path + "_map.png")

        if draw_tracepoints :
            if reset:
                figure = plt.figure(figsize=(20, 20))

            mapconnectiongraph = None
            nx.draw_networkx(traceconnectiongraph, pos, False, node_color=node_colors)
            nx.draw_networkx_edge_labels(traceconnectiongraph, pos, font_size=5)

            plt.savefig(path + "_trace.png")
    
    def getcommondecimalplaces(self):
        commonplaceslat = Decimal("inf")
        commonplaceslon = Decimal("inf")
        for point in self.mappoints:
            (lat,lon) = point.asquantizedtuple()
            for opoint in self.mappoints:
                if opoint == point:
                    continue
                (olat, olon) = opoint.asquantizedtuple()
                placeslat = self.cmpdecimalplaces(lat, olat)
                placeslon = self.cmpdecimalplaces(lon, olon)
                
                if placeslat < commonplaceslat:
                    commonplaceslat = placeslat
                if placeslon < commonplaceslon:
                    commonplaceslon = placeslon
        return (commonplaceslat, commonplaceslon)
                
    def cmpdecimalplaces(self, x, y):
        assert isinstance(x, Decimal)
        assert isinstance(y, Decimal)
        
        digitsx = x.as_tuple().digits
        digitsy = y.as_tuple().digits
        
        for i in range(len(digitsx)):
            if digitsx[i] != digitsy[i]:
                return i
        return len(digitsx)
    
    def _cutdecimalplaces(self, point, placeslat, placeslon):
        assert not (placeslat is None)
        assert not (placeslon is None)
        (lat, lon ) = point.asquantizedtuple()
        return [self._cutdecimalplace(lat, placeslat), 
                self._cutdecimalplace(lon, placeslon)]
    
    '''
    @summary: Cut n digits from decimal x starting at the front
    '''
    def _cutdecimalplace(self, x, n):
        assert isinstance(x, Decimal)
        # try to keep 2 decimal places max
        ndigits = len(x.as_tuple().digits)
        if n > ndigits:
            pass
        assert not n > ndigits
        
        digits = x.as_tuple().digits[n:]
        nremainingdigits = len(digits)
                
        if nremainingdigits >= 4: exp = -2
        elif nremainingdigits == 3: exp = -1
        else: exp = 0
        return Decimal((0, digits, exp))
                

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

        oldconnections = copy(self.connections)
        visitedconnections = []
        unvisitedconnections = self.connections

        while unvisitedconnections:

            minimalcost = [(connection.totalcost, connection) for connection in unvisitedconnections]
            heapq.heapify(minimalcost)

            (cost, connection) = heapq.heappop(minimalcost)
            # the rest cannot be reached from here
            if connection.totalcost == Decimal("Infinity"):
                break
            visitedconnections.append(connection)
            unvisitedconnections.remove(connection)

            successors = self.getallconnections(connection.maptarget)

            for successor in successors:
                self.relax(connection, successor)
                
        self.connections = oldconnections

    def getshortesttrack(self, source, target):
        self.logger.info("Starting single source shortest path from %d to %d" % (source.id, target.id))
        self.shortesttrack(source)
        self.logger.info("Finshed single source shortest path")
        shortesttrack = MapConnectionTrace()
        currentconnection = None
        totalcost = None
        totarget = self.getallconnections(target=target)


        self.logger.info("Searching cheapest end connection")
        for connection in totarget:
            if connection.totalcost < totalcost or totalcost == None:
                currentconnection = connection
                totalcost = connection.totalcost

        if not totarget or totalcost == Decimal("Infinity"):
            self.logger.info("Did not find a connection to the target point")
            return shortesttrack

        self.logger.info("Found %s with totalcost %s" % (currentconnection, str(totalcost)))
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

            currenttrack = MapPointTrace()
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

            currenttrack = MapPointTrace()
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


