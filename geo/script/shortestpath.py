'''
Created on Feb 7, 2013

@author: fredo
'''

from geo.routing.graph import Graph
from geo.io.jsonx import JSONX

g = Graph.getinstance(0)
source = g.getmappoint(pointid=17)
target = g.getmappoint(pointid=25)

track = g.getshortesttrack(source, target)
print vars(track)
json = JSONX()
json.setconnectiontrack(track, g)
print json.getjson()
