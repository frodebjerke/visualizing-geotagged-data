'''
Created on Oct 25, 2012

@author: fredo
'''

from geo.osm import OSM
from geo.routing.graph import Graph
from filldb import tracktovideo
from django.conf import settings
import os

def drawmap(mode, filename):
#    geocoder = OSM(1)
#    nodes = geocoder.getnodes()
    graph = Graph.getinstance(mode)
#    for node in nodes:
#        graph.insertmappoint(node[0],node[1])
    if filename is None:
        filename = "%d" % mode
    graph.draw(os.path.join(settings.OUT_DIR, filename),reset = False)


if __name__ == "__main__":
    drawmap(0)