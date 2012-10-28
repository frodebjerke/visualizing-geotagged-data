'''
Created on Oct 25, 2012

@author: fredo
'''

from geo.osm import OSM
from geo.routing.graph import Graph
from django.conf import settings
import os

def drawmap():
    geocoder = OSM()
    nodes = geocoder.getnodes()
    graph = Graph.getinstance(3)
    for node in nodes:
        graph.insertmappoint(node[0],node[1])
    graph.draw(os.path.join(settings.TEST_PATH,"mannheim-streets"))
    

if __name__ == "__main__":
    drawmap()