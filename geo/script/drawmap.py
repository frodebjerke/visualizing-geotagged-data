'''
Created on Oct 25, 2012

@author: fredo
'''

from geo.osm import OSM
from geo.map.map import Map
from django.conf import settings
import os

def drawmap():
    geocoder = OSM()
    nodes = geocoder.getnodes()
    network = Map.getinstance(3)
    for node in nodes:
        network.insertmappoint(node[0],node[1])
    network.draw(os.path.join(settings.TEST_PATH,"mannheim-streets"))
    

if __name__ == "__main__":
    drawmap()