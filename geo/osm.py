'''
Created on Mar 20, 2012

Based on python-nominatim by agabel 
https://github.com/agabel/python-nominatim

@author: fredo
'''


from geo.exceptions import OSMException
from geo.routing.util import ConnectionMode
from xml.dom import minidom
from decimal import Decimal
import urllib
from django.conf import settings
import json
import os, sys, math
from decimal import Decimal
import logging
import copy

def calculate_distance(coord1,coord2):
    lat1,lon1 = (coord1[0],coord1[1])
    lat2,lon2 = (coord2[0],coord2[1])
    lon1, lat1, lon2, lat2 = map(math.radians , [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a)) 
    km = 6367 * c
    return km 

class OSM():
    """
    @author: Frederik Claus
    @summary: Uses a local .osm files that contains only nodes from highways. This is highly inefficient.
    """
    MANNHEIM_OSM = os.path.join(settings.MAP_DIR, "mannheim-streets.osm")
    N_LOOK_AHEAD = 3
    MAX_TRIES = 3
    SIGMA = Decimal(0.010) #10 meter
    logger = logging.getLogger(__name__)
    
    def __init__(self, mode):
        self.mode = mode
#        try:
        doc = minidom.parse(os.path.join(settings.MAP_DIR, "%d.osm" % mode))
#            doc = minidom.parse(os.path.join(settings.MAP_DIR,"mannheim-streets.osm"))
        ways = doc.getElementsByTagName("way")
        nodes = doc.getElementsByTagName("node")
        if mode != ConnectionMode.TRAIN:
            bidirectional = True
        else:
            bidirectional = False
            
        self.graph = OSMGraph(nodes, ways, bidirectional = bidirectional)
            
#            for node in nodes:
#                self.nodes.append((Decimal(node.getAttribute("lat")),Decimal(node.getAttribute("lon"))))
#        except Exception as e:
#            raise OSMException, "Could not parse osm file: %s" % str(e)
    
    def getnodes(self):
        return self.nodes;
    
    def reversegeocode(self, coordinates):
        """
        @param coordinates: Triple containing <lat,lon,time>
        """
        blacklist = []
        index = 0
        finished = False
        n_coordinates = len(coordinates)
        predecessors = []
        tries = 0
        
        while not finished:
            coordinate = coordinates[index]
            self.logger.debug("Getting coordinate %s" % str(coordinate))
            
            if len(predecessors) == 0:
                self.logger.debug("Start of the trace. No other coordinate looked at yet.")
                current = self.simple_resolve(coordinate)
        
            else:
                predecessor = predecessors[-1]
                predecessor_distance = calculate_distance(predecessor, coordinate)
                try:
                    current = self.graph_resolve(predecessor, coordinate, blacklist)
                except OSMException, e:
                    current = None
                if current is None: #look_ahead blacklisted the node
                    try:
                        self.logger.debug("Can't resolve with graph, all blacklisted. Trying simple with blacklist.")
                        current = self.simple_resolve(coordinate,blacklist)
                        tries += 1
                    except OSMException, e:
                        self.logger.debug("Can't resolve with simple resolving either. Resolve without blacklist.")
                        ignore_distance = True
                        current = self.simple_resolve(coordinate)
                        
                current_distance = calculate_distance(current, coordinate)
        
                """ looking backward """
                if predecessor_distance < current_distance: #we are going in the wrong way or are still at the same point
#                    if abs(self.calculate_distance(predecessor, coordinates[index-1]) - predecessor_distance) < self.calculate_distance(predecessor, current): #still at the same point
                    if abs(current_distance - predecessor_distance) < calculate_distance(predecessor, current): #still at the same point
#                    if (self.calculate_distance(predecessor, coordinates[index+1]) - predecessor_distance) < self.SIGMA:
                        self.logger.debug("Staying on the same node.")
                        current = (predecessor[0],predecessor[1],current[2],predecessor[3])
                    elif calculate_distance(predecessor, coordinates[index+1]) < predecessor_distance:
                        self.logger.debug("Waiting for the trace to catch up")
                        current = (predecessor[0],predecessor[1],current[2],predecessor[3])
                    else: #going the wrong way, only in train mode
                        self.logger.debug("Going the wrong way. Blacklisting node.")
                        predecessor_coordinate = coordinates[index - 1]
                        if predecessor not in blacklist:
                            blacklist.append(predecessor)#add to the blacklist
                        new_predecessor = self.simple_resolve(predecessor_coordinate, blacklist) #get another node close to the predecessor
                        if new_predecessor is None: #there is no good solution. stick to the best one
                            new_predecessor = self.simple_resolve(predecessor_coordinate)
                        predecessors[-1] = new_predecessor
                        continue # try again
#                    else:
#                        self.logger.debug("Not in train mode. Try the other direction")
#                        current = self.graph_resolve(predecessor, coordinate, blacklist, reverse = True)
#===========================================================================
# this is problematic, because while the user is standing still it will tag the trace as wrong
#===========================================================================
#                else:
#                    """ looking forward """
#                    distances = self.look_ahead(coordinates, index, current)
#            
#                    if ignore_distance or tries >= self.MAX_TRIES:
#                        self.logger.info("Distance is getting bigger, but there is no alternative route.")
#                    elif self.gapping_apart(distances): #we are on a suboptimal trace
#                        self.logger.debug("Distance in getter bigger. Blacklisting current node")
#                        if not current in blacklist: 
#                            blacklist.append(current) 
#                        continue #try again
    
            index += 1
            tries = 0
            ignore_distance = False
            self.logger.debug("Appending %s." % str(current))
            predecessors.append(current) #everything is fine
    
            if index >= n_coordinates:
                finished = True
                
        return predecessors 
        
    def gapping_apart(self,distances):
        bigger = False
        for index in range(len(distances)):
            if index == len(distances) - 1:
                break
            if not(distances[index + 1] - distances[index ] > self.SIGMA) : #the next distance is not significantly bigger than the current one
                return False
        return True


    def look_ahead(self,coordinates, current_index, predecessor):
        successor = None
        successors = []
        distances = []
        
        n_last = len(coordinates) - (1+current_index)
        
        if n_last > self.N_LOOK_AHEAD:
            n_last = self.N_LOOK_AHEAD
        
        for index in range(n_last):
            coordinate = coordinates[current_index + (index + 1)]
            if len(successors) != 0:
                predecessor = successors[-1 ]
            current = self.graph_resolve(predecessor, coordinate)
            successors.append(current) 
            distance = calculate_distance(current, coordinate)
            distances.append(distance)

        return distances
    
    def simple_resolve(self, coordinate, blacklist = None):
        """
        @summary: Performs a lookup and return the nearest address
        @param param: tuple <lat,lon,time>
        @return: tuple <lat,lon,time,id> 
        """
        if not blacklist:
            blacklist = []
        return self.graph.simple_resolve(coordinate, blacklist)
    
    def graph_resolve(self, start, coordinate, blacklist = None):
        """
        @param coordinate: tuple <lat,lon,time,id>
        @return: tuple <lat,lon,time,id>
        """        
        return self.graph.resolve(start, coordinate,blacklist)
    
    
#        return (lat1-lat2)**2 + (lon1 - lon2)**2
        
class OSMGraph():
    
    logger = logging.getLogger(__name__)
    
    def __init__(self, nodes, ways, bidirectional = False):
        self.nodes = {}
        for node in nodes:
            osmnode = OSMNode(node)
            self.nodes[osmnode.id] = osmnode
            if bidirectional:
                relabeled = OSMNode(node,relabel = True)
                self.nodes[relabeled.id] = relabeled
        for way in ways:
            nds = way.getElementsByTagName("nd")
            self.add_way(nds)
            if bidirectional:
                nds.reverse()
                self.add_way(nds, relabel = True)
                
    def add_way(self, nds, relabel = False):
        predecessor = None
        for nd in nds:
            if relabel:
                id = "%s_RELABEL" % nd.getAttribute("ref")
            else:
                id = nd.getAttribute("ref")
            node = self.nodes[id]
            
            if predecessor != None:    
                self.nodes[predecessor.id].add_successor(node)
                
            predecessor = node
                    
    def resolve(self,start, coordinate,blacklist):
        """
        @param coordinate: tuple <lat,lon,time,id>
        @return: tuple <lat,lon,time,id>
        """
        start = self.nodes[start[3]]
        if not blacklist:
            blacklist = []
        return self.simple_resolve(coordinate, blacklist, start.successors)
                           
    def simple_resolve(self,coordinate,blacklist, nodes = None):
        """
        @summary: Performs a lookup and return the nearest address
        @param param: tuple <lat,lon,time>
        @return: tuple <lat,lon,time,id> 
        """
        min_distance = sys.maxint
        min_node = None
        
        if not nodes:
            nodes = self.nodes.values()
        
        for node in nodes:
            blacklisted = False
            for black_node in blacklist:
                if black_node[0] == node.lat and black_node[1] == node.lon:
                    blacklisted = True
                    break
            if blacklisted:
                self.logger.debug("Skipping blacklisted node %s." % str(node))
                continue
            
            distance = calculate_distance(coordinate, (node.lat, node.lon))
#            self.logger.debug("Comparing %f to %f." % (distance, min_distance))
            if distance < min_distance:
                min_distance = distance
                min_node = node
        
        if min_node is None:
            raise OSMException, "Could not find a nearby node!"    
        return (min_node.lat,min_node.lon,coordinate[2],min_node.id)
    

class OSMNode():
    def __init__(self, node, relabel = False):
        if relabel:
            self.id = "%s_RELABEL" % node.getAttribute("id")
        else:
            self.id = node.getAttribute("id")
        self.lat = Decimal(node.getAttribute("lat"))
        self.lon = Decimal(node.getAttribute("lon"))
        self.successors = []
    def add_successor(self, node):
        if node in self.successors:
            return
        self.successors.append(node)

class OSMLegacy():
    """Nominatim never returns any error message. 
        It tries to match with the Point that is closest, even if no parameters are given"""
    
    BASE_URL = "http://nominatim.openstreetmap.org/"
    REVERSE_URL = BASE_URL + "reverse?format=json&%s"
    
    def reversegecode(self, lat, lon, zoom=18):
        """Performs a lookup and return the nearest adress"""
        params = {}
        params["lat"] = str(lat)
        params["lon"] = str(lon)
        params["zoom"] = zoom
        
        
        url = self.REVERSE_URL % urllib.urlencode(params)
        try :
            data = urllib.urlopen(url)
            response = data.read()
            
            data = self.parse_json(response)
            
            return (Decimal(data["lat"]), Decimal(data["lon"]), data["display_name"])
        
        except IOError, e:
            raise OSMException , str(e)
        
    def parse_json(self, data):
        try:
            data = json.loads(data)
        except:
            data = []
        
        return data

if __name__ == "__main__":
    osm = OSM()
    print osm.reversegecode("49.1231231", "-1.123123", 18)
    




