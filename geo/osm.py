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
from copy import deepcopy, copy
import logging

    
logger = logging.getLogger(__name__)

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
        self.state = None
            
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
        index = 0
        finished = False
        n_coordinates = len(coordinates)
        predecessors = []
        is_backjumped = False
        
        while not finished:
            coordinate = coordinates[index]
            logger.debug("Getting coordinate %s" % str(coordinate))
            
            if len(predecessors) == 0:
                logger.debug("Start of the trace. No other coordinate looked at yet.")
                current = self.graph_resolve(coordinate)
                self.view.add(current)
        
            else:
                predecessor = predecessors[-1]
                try:
                    current = self.subgraph_resolve(predecessor, coordinate)
                    # that seems to be the right way
                    if current != predecessor:
                        if predecessor.is_adjacent(current):
                            self.save(current, {"index": index,
                                       "predecessors": copy(predecessors),
                                       "current" : predecessor})
                            is_backjumped = False
                            #we first need to add the new node so it is not removed
                            self.view.add(current)
                            #blacklist the predecessor and remove all nodes that cant be reache anymore
                            self.view.blacklist(predecessor)
                            
                        # that seems to be the wrong way
                        else:
                            #we already jumped back once
                            #the gpx file is probably off
                            if is_backjumped:
                                self.view.blacklist(current)
                                continue
                            
                            state = self.restore(predecessor)
                            is_backjumped = True
#                            current = predecessor
                            #never use predecessor again
                            self.view.blacklist(predecessor)
                            current = state["current"]
                            predecessor = None
                            predecessors = state["predecessors"]
                            index = state["index"]
                            continue
                    
                except OSMException, e:
                    raise e
                
#            if not self.view.is_visited(current):
#                self.view.add(current)
                  
#                if current is None: #look_ahead blacklisted the node
#                    try:
#                        self.logger.debug("Can't subgraph_resolve with _resolve, all blacklisted. Trying simple with blacklist.")
#                        current = self._resolve(coordinate,blacklist)
#                        tries += 1
#                    except OSMException, e:
#                        self.logger.debug("Can't subgraph_resolve with simple resolving either. Resolve without blacklist.")
#                        ignore_distance = True
#                        current = self._resolve(coordinate)
#                        
#                current_distance = calculate_distance(current, coordinate)
        
#                """ looking backward """
#                if predecessor_distance < current_distance: #we are going in the wrong way or are still at the same point
##                    if abs(self.calculate_distance(predecessor, coordinates[index-1]) - predecessor_distance) < self.calculate_distance(predecessor, current): #still at the same point
#                    if abs(current_distance - predecessor_distance) < calculate_distance(predecessor, current): #still at the same point
##                    if (self.calculate_distance(predecessor, coordinates[index+1]) - predecessor_distance) < self.SIGMA:
#                        self.logger.debug("Staying on the same node.")
#                        current = (predecessor[0],predecessor[1],current[2],predecessor[3])
#                    elif calculate_distance(predecessor, coordinates[index+1]) < predecessor_distance:
#                        self.logger.debug("Waiting for the trace to catch up")
#                        current = (predecessor[0],predecessor[1],current[2],predecessor[3])
#                    else: #going the wrong way, only in train mode
#                        self.logger.debug("Going the wrong way. Blacklisting node.")
#                        predecessor_coordinate = coordinates[index - 1]
#                        if predecessor not in blacklist:
#                            blacklist.append(predecessor)#add to the blacklist
#                        new_predecessor = self._resolve(predecessor_coordinate, blacklist) #get another node close to the predecessor
#                        if new_predecessor is None: #there is no good solution. stick to the best one
#                            new_predecessor = self._resolve(predecessor_coordinate)
#                        predecessors[-1] = new_predecessor
#                        continue # try again
#                    else:
#                        self.logger.debug("Not in train mode. Try the other direction")
#                        current = self.subgraph_resolve(predecessor, coordinate, blacklist, reverse = True)
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
            logger.debug("Appending %s." % current.id)
            predecessors.append(current) #everything is fine
    
            if index >= n_coordinates:
                finished = True
                
        return [(node.lat,node.lon,coordinate[2],node.id) for (node, coordinate) in zip(predecessors, coordinates)]
        
#    def gapping_apart(self,distances):
#        bigger = False
#        for index in range(len(distances)):
#            if index == len(distances) - 1:
#                break
#            if not(distances[index + 1] - distances[index ] > self.SIGMA) : #the next distance is not significantly bigger than the current one
#                return False
#        return True


#    def look_ahead(self,coordinates, current_index, predecessor):
#        successor = None
#        successors = []
#        distances = []
#        
#        n_last = len(coordinates) - (1+current_index)
#        
#        if n_last > self.N_LOOK_AHEAD:
#            n_last = self.N_LOOK_AHEAD
#        
#        for index in range(n_last):
#            coordinate = coordinates[current_index + (index + 1)]
#            if len(successors) != 0:
#                predecessor = successors[-1 ]
#            current = self.subgraph_resolve(predecessor, coordinate)
#            successors.append(current) 
#            distance = calculate_distance(current, coordinate)
#            distances.append(distance)
#
#        return distances
    
    def save(self, jumped_to, state):
#        assert not self.state.has_key(jumped_to.id)
        self.state = (state, self.view.copy())
        
        
    def restore(self, back_to):
#        assert self.state.has_key(back_to.id)
        (state, self.view) = self.state
        return state
        
    
    def graph_resolve(self, coordinate):
        """
        @summary: Performs a lookup and return the nearest address
        @param param: tuple <lat,lon,time>
        @return: tuple <lat,lon,time,id> 
        """
        self.view = OSMGraphView()
        return self.graph.graph_resolve(coordinate)
    
    def subgraph_resolve(self, start, coordinate):
        """
        @param coordinate: tuple <lat,lon,time,id>
        @return: tuple <lat,lon,time,id>
        """
        nodes = self.view.as_nodes()
        return self.graph.subgraph_resolve(start, coordinate, nodes)
    
    
#        return (lat1-lat2)**2 + (lon1 - lon2)**2
        
class OSMGraph():
    

    def __init__(self, nodes, ways, bidirectional = False):
        self.nodes = {}
        self.state = {}
        for node in nodes:
            osmnode = OSMNode(node)
            self.nodes[osmnode.id] = osmnode
#            if bidirectional:
#                relabeled = OSMNode(node,relabel = True)
#                self.nodes[relabeled.id] = relabeled
        for way in ways:
            nds = way.getElementsByTagName("nd")
            self.add_way(nds)
            if bidirectional:
                nds.reverse()
#                self.add_way(nds, relabel = True)
                self.add_way(nds)
                
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
            
    def graph_resolve(self, coordinate):
        nodes = self.nodes.values()
        return self._resolve(coordinate, nodes)
        
                    
    def subgraph_resolve(self,start, coordinate, nodes):
        """
        @param coordinate: tuple <lat,lon,time,id>
        @return: tuple <lat,lon,time,id>
        """
        return self._resolve(coordinate, nodes)
                           
    def _resolve(self,coordinate, nodes):
        """
        @summary: Performs a lookup and return the nearest address
        @param param: tuple <lat,lon,time>
        @return: tuple <lat,lon,time,id> 
        """
        min_distance = sys.maxint
        min_node = None
        
        for node in nodes:
#            if node in blacklist:
#                logger.debug("Skipping blacklisted node %s." % str(node))
#                continue
            
            distance = calculate_distance(coordinate, (node.lat, node.lon))
#            self.logger.debug("Comparing %f to %f." % (distance, min_distance))
            if distance < min_distance:
                min_distance = distance
                min_node = node
        
        if min_node is None:
            raise OSMException, "Could not find a nearby node!"  
        
            
              
#        return (min_node.lat,min_node.lon,coordinate[2],min_node.id)
        return min_node
    
 

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
    def is_adjacent(self, node):
        return node in self.successors
    def __eq__(self, other):
        if isinstance(other, OSMNode):
            return self.id == other.id
        return False
    def __hash__(self):
        return int(self.id)
    def __str__(self):
        return self.id
    def __repr__(self):
        return self.id
    



class OSMGraphView():
    def __init__(self):
        self.visited = []
        self.nodes = set()
        self._blacklist = []
        
    def copy(self):
        other = OSMGraphView()
        for node in self.visited:
            other.add(node)
        return other
    
    def add(self, node):
        assert not node in self._blacklist
        assert not node in self.visited
        self.visited.append(node)
        self.nodes.add(node)
        logger.debug("Adding node %s." % node)
        for successor in node.successors:
            logger.debug("Adding neighbour %s." % successor)
            self.nodes.add(successor)
            
    def blacklist(self, node):
        logger.debug("Blacklisting node %s." % node)
        self._blacklist.append(node)
#        self._remove_neighbours(node)
        

    def as_nodes(self):
        nodes = []
        for node in self.nodes:
            if node in self._blacklist:
                continue
            nodes.append(node)
        return nodes
    
    def remove_node(self, node):
        self.visited.remove(node)
        self._remove_neighbours(node)
        
                
    def _remove_neighbours(self, node):
        for neighbour in node.successors:
            if neighbour in self.visited:
                continue
            remove = True
            for neighbours_neighbour in [neighbour_neighbour for neighbour_neighbour in neighbour.successors if neighbour_neighbour != node]:
                if neighbours_neighbour in self.visited:
                    remove = False
                    break
            if remove and neighbour in self.nodes:
                logger.debug("Removing node %s." % neighbour)
                self.nodes.remove(neighbour)
                
    def is_visible(self, node):
        return node in self.nodes
    
    def is_visited(self, node):
        return node in self.visited
    




#class LocationGraph():
#    """
#    @summary All input nodes must have an id attribute
#    """
#    def __init__(self):
#        self.visited = []
#        self.nodes = {}
#        
#    def add(self, node):
#        self.nodes[node.id] = LocationNode(node.id)
#        self.set_visited(node.id)
#    
#    def set_visited(self, node):
#        assert self.nodes.has_key(node.id)
#        self.visited.append(self.nodes[node.id])
#        
#    def add_neighbours(self, node, neighbours):
#        """
#        @param neighbours: dictionary that has an id key
#        """ 
#        assert node.id
#        neighbours = [self.nodes[neighbour.id] for neighbour in neighbours]
#        node = self.nodes[node.id]
#        node.add_neighbours(neighbours)
#        
#    def get_neighbours(self, node):
#        assert self.nodes.has_key(node.id)
#        node = self.nodes[node.id]
#        return node.get_neighbours()
#
#
#class LocationNode():
#    def __init__(self, node_id):
#        self.id = node_id
#        self.neighbours = {}
#    def add_neighbours(self,neighbours):
#        for neighbour in neighbours:
#            if self.neighbours.has_key(neighbour.id):
#                continue
#            self.neighbour[neighbour.id] = neighbour
#    def get_neighbours(self):
#        return self.get_neighbours()

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
    




