'''
Created on Mar 30, 2012

@author: fredo
'''

from geo.map.map import Map
from django.conf import settings
from geo.script.gpxtogeocode import filetodto
from geo.map.connectionmode import ConnectionMode
import os


TRACK_PATH = os.path.join(settings.TEST_PATH, "tracks")
VIDEO_PATH = os.path.join(settings.STATIC_PATH, "upload")

#===============================================================================
# Track paths
#===============================================================================
PARADEPLATZ_WASSERTURM_FUSS_TRACK = os.path.join(TRACK_PATH, "t2.geocode")
SCHLOSS_MARKTPLATZ_FUSS_TRACK = os.path.join(TRACK_PATH, "t4.geocode")
SCHLOSS_PARADEPLATZ_FUSS_TRACK = os.path.join(TRACK_PATH, "t5.geocode")

PARADEPLATZ_WASSERTURM_TRAM_TRACK = os.path.join(TRACK_PATH, "t1.geocode")
SCHLOSS_MARKTPLATZ_TRAM_TRACK = os.path.join(TRACK_PATH, "t3.geocode")
SCHLOSS_PARADEPLATZ_TRAM_TRACK = os.path.join(TRACK_PATH, "t6.geocode")
#===============================================================================
# Video paths
#===============================================================================
PARADEPLATZ_WASSERTURM_FUSS_VIDEO = os.path.join(VIDEO_PATH, "v5.ogv")
SCHLOSS_MARKTPLATZ_FUSS_VIDEO = os.path.join(VIDEO_PATH, "v4.ogv")
SCHLOSS_PARADEPLATZ_FUSS_VIDEO = os.path.join(VIDEO_PATH, "v2.ogv")

PARADEPLATZ_WASSERTURM_TRAM_VIDEO = os.path.join(VIDEO_PATH, "v1.ogv")
SCHLOSS_MARKTPLATZ_TRAM_VIDEO = os.path.join(VIDEO_PATH, "v3.ogv")
SCHLOSS_PARADEPLATZ_TRAM_VIDEO = os.path.join(VIDEO_PATH, "v6.ogv")


tracktovideo = {
                PARADEPLATZ_WASSERTURM_FUSS_TRACK : [ConnectionMode.WALK, PARADEPLATZ_WASSERTURM_FUSS_VIDEO],
                PARADEPLATZ_WASSERTURM_TRAM_TRACK : [ConnectionMode.TRAIN, PARADEPLATZ_WASSERTURM_TRAM_VIDEO],
                SCHLOSS_MARKTPLATZ_FUSS_TRACK : [ConnectionMode.WALK, SCHLOSS_MARKTPLATZ_FUSS_VIDEO],
                SCHLOSS_MARKTPLATZ_TRAM_TRACK : [ConnectionMode.TRAIN, SCHLOSS_MARKTPLATZ_TRAM_VIDEO],
                SCHLOSS_PARADEPLATZ_FUSS_TRACK : [ConnectionMode.WALK, SCHLOSS_PARADEPLATZ_FUSS_VIDEO],
                SCHLOSS_PARADEPLATZ_TRAM_TRACK : [ConnectionMode.TRAIN, SCHLOSS_PARADEPLATZ_TRAM_VIDEO]}

def insertall():
    for trackpath in tracktovideo.keys():
        dtos = filetodto(open(trackpath, "r"), tracktovideo[trackpath][1])
        map = Map.getinstance(tracktovideo[trackpath][0])
        map.inserttracepoints(dtos)

