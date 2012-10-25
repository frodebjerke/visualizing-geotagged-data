'''
Created on Mar 20, 2012

Based on python-nominatim by agabel 
https://github.com/agabel/python-nominatim

@author: fredo
'''

from geo.coder import Coder
from geo.exception import OSMException
from xml.dom import minidom
from decimal import Decimal
import urllib
from django.conf import settings
import json
import os,sys,math
from decimal import Decimal
import logging

class OSM(Coder):
    """
    @author: Frederik Claus
    @summary: Uses a local .osm files that contains only nodes from highways. This is highly inefficient.
    """
    MANNHEIM_OSM = os.path.join(settings.MAP_DIR,"mannheim-streets.osm")
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        try:
            self.nodes = []
            doc = minidom.parse(self.MANNHEIM_OSM)
            nodes = doc.getElementsByTagName("node")
            for node in nodes:
                self.nodes.append((Decimal(node.getAttribute("lat")),Decimal(node.getAttribute("lon"))))
        except Exception as e:
            raise OSMException, "Could not parse osm file: %s" % str(e)
    
    def getnodes(self):
        return self.nodes;
    
    def reversegecode(self,lat,lon):
        """
        @summary: Performs a lookup and return the nearest address
        """
        min_distance = sys.maxint
        min_node = None
        
        for node in self.nodes:
            distance = self._getdistance(lat,lon,node[0],node[1])
#            self.logger.debug("Comparing %f to %f." % (distance, min_distance))
            if distance < min_distance:
                min_distance = distance
                min_node = node
        
        if min_node is None:
            raise OSMException, "Could not find a nearby node!"
        
        return min_node
        
    def _getdistance(self,lat1,lon1,lat2,lon2):
        lon1, lat1, lon2, lat2 = map(math.radians , [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        km = 6367 * c
        return km 
#        return (lat1-lat2)**2 + (lon1 - lon2)**2
        
    
class OSMLegacy(Coder):
    """Nominatim never returns any error message. 
        It tries to match with the Point that is closest, even if no parameters are given"""
    
    BASE_URL = "http://nominatim.openstreetmap.org/"
    REVERSE_URL = BASE_URL + "reverse?format=json&%s"
    
    def reversegecode(self,lat,lon,zoom = 18):
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
            
            return (Decimal(data["lat"]),Decimal(data["lon"]),data["display_name"])
        
        except IOError,e:
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
    




