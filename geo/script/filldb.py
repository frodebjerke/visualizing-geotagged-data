'''
Created on Mar 30, 2012

@author: fredo
'''

from geo.routing.graph import Graph
from django.conf import settings
from geo.script.gpxtogeocode import filetodto
from geo.routing.util import ConnectionMode
import os,glob


TRACK_DIR = os.path.join(settings.RES_DIR, "tracks")
VIDEO_DIR = os.path.join(settings.STATIC_PATH, "upload")
VIDEO_PATH = os.path.join(settings.TEST_PATH, "video.3gp")

#===============================================================================
# Track paths
#===============================================================================
SCHLOSS_PARADEPLATZ_FUSS_TRACK = os.path.join(TRACK_DIR, "schloss_paradeplatz_0.geocode")
PARADEPLATZ_MARKTPLATZ_FUSS_TRACK = os.path.join(TRACK_DIR, "paradeplatz_marktplatz_0.geocode")
MARKTPLATZ_PARADEPLATZ_FUSS_TRACK = os.path.join(TRACK_DIR, "marktplatz_paradeplatz_0.geocode")
PARADEPLATZ_SCHLOSS_FUSS_TRACK = os.path.join(TRACK_DIR, "paradeplatz_schloss_0.geocode")


PARADEPLATZ_WASSERTURM_TRAM_TRACK = os.path.join(TRACK_DIR, "t1.geocode")
SCHLOSS_MARKTPLATZ_TRAM_TRACK = os.path.join(TRACK_DIR, "t3.geocode")
SCHLOSS_PARADEPLATZ_TRAM_TRACK = os.path.join(TRACK_DIR, "t6.geocode")
#===============================================================================
# Video paths
#===============================================================================
SCHLOSS_PARADEPLATZ_FUSS_VIDEO = os.path.join(VIDEO_DIR, "schloss_paradeplatz_0.ogv")
PARADEPLATZ_MARKTPLATZ_FUSS_VIDEO = os.path.join(VIDEO_DIR, "paradeplatz_marktplatz_0.ogv")
MARKTPLATZ_PARADEPLATZ_FUSS_VIDEO = os.path.join(VIDEO_DIR, "marktplatz_paradeplatz_0.ogv")
PARADEPLATZ_SCHLOSS_FUSS_VIDEO = os.path.join(VIDEO_DIR, "paradeplatz_schloss_0.ogv")

PARADEPLATZ_WASSERTURM_TRAM_VIDEO = os.path.join(VIDEO_DIR, "v1.ogv")
SCHLOSS_MARKTPLATZ_TRAM_VIDEO = os.path.join(VIDEO_DIR, "v3.ogv")
SCHLOSS_PARADEPLATZ_TRAM_VIDEO = os.path.join(VIDEO_DIR, "v6.ogv")


#tracktovideo = {
#                PARADEPLATZ_WASSERTURM_FUSS_TRACK : [ConnectionMode.WALK, PARADEPLATZ_WASSERTURM_FUSS_VIDEO],
#                SCHLOSS_MARKTPLATZ_FUSS_TRACK : [ConnectionMode.WALK, SCHLOSS_MARKTPLATZ_FUSS_VIDEO],
#                SCHLOSS_PARADEPLATZ_FUSS_TRACK : [ConnectionMode.WALK, SCHLOSS_PARADEPLATZ_FUSS_VIDEO],
#                
##                SCHLOSS_PARADEPLATZ_TRAM_TRACK : [ConnectionMode.TRAIN, SCHLOSS_PARADEPLATZ_TRAM_VIDEO],
##                SCHLOSS_MARKTPLATZ_TRAM_TRACK : [ConnectionMode.TRAIN, SCHLOSS_MARKTPLATZ_TRAM_VIDEO],
##                PARADEPLATZ_WASSERTURM_TRAM_TRACK : [ConnectionMode.TRAIN, PARADEPLATZ_WASSERTURM_TRAM_VIDEO],
#                }
tracktovideo = [
                [SCHLOSS_PARADEPLATZ_FUSS_TRACK, 0, SCHLOSS_PARADEPLATZ_FUSS_VIDEO],
                [PARADEPLATZ_MARKTPLATZ_FUSS_TRACK, 0, PARADEPLATZ_MARKTPLATZ_FUSS_VIDEO],
                [MARKTPLATZ_PARADEPLATZ_FUSS_TRACK, 0, MARKTPLATZ_PARADEPLATZ_FUSS_VIDEO],
                [PARADEPLATZ_SCHLOSS_FUSS_TRACK, 0, PARADEPLATZ_MARKTPLATZ_FUSS_VIDEO],
                
                [SCHLOSS_MARKTPLATZ_TRAM_TRACK, 1, SCHLOSS_MARKTPLATZ_TRAM_VIDEO],
                [PARADEPLATZ_WASSERTURM_TRAM_TRACK, 1, PARADEPLATZ_WASSERTURM_TRAM_VIDEO],
                ]

def insertall():
    """
    @summary: Inserts already geocoded traces into the db
    """
    for track in tracktovideo:
        dtos = filetodto(open(track[0], "r"), track[2])
        graph = Graph.getinstance(track[1])
        graph.inserttracepoints(dtos)

def insertevaluation():
    insertdir(settings.EVALUATION_DIR)

from geo.test.map import VIDEO_PATH 
        
def insertdir(geocodepath, videopath = VIDEO_PATH, afterinsert = False ):
    count = 0
    for trace in glob.glob("%s/*.geocode" % geocodepath):
        dtos = filetodto(open(trace,"r"), videopath)
        map = Graph.getinstance(0)
        map.inserttracepoints(dtos)
        if afterinsert:
            yield "%d-%s" % (count, os.path.basename(trace))
            count += 1
        
if __name__ == "__main__":
    insertall()