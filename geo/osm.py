'''
Created on Mar 20, 2012

Based on python-nominatim by agabel 
https://github.com/agabel/python-nominatim

@author: fredo
'''

from geo.coder import Coder
from geo.exception import OSMException
from decimal import Decimal
import urllib

import simplejson

class OSM(Coder):
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
            data = simplejson.loads(data)
        except simplejson.JSONDecodeError:
            data = []
        
        return data

if __name__ == "__main__":
    osm = OSM()
    print osm.reversegecode("49.1231231", "-1.123123", 18)
    




