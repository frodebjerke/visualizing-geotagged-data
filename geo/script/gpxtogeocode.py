'''
Created on Mar 23, 2012

@author: fredo
'''

from geo.coordinate.gpx import GPX
from geo.osm import OSM
from geo.model.videofactory import VideoFactory
from geo.map.tracepointdto import TracePointDTO
from django.conf import settings
from geo.coordinate.videotime import videotimes

import os
import pickle
from geo.web.logger import getLogger

def resolvefile(inpath, outpath):
    logger = getLogger(__name__)
    gpx = GPX(open(inpath, "r"))
    osm = OSM()

    geocodes = []
    if not gpx.isvalid():
        raise RuntimeError, "gpx file is not valid"
    for (lat, lon, time) in gpx.gettrackpoint():
        (lat, lon, address) = osm.reversegecode(lat=lat, lon=lon)
        geocodes.append((lat,
                         lon,
                         address,
                         time))
        logger.debug("Processed %s, %s" % (lat, lon))
    out = open(outpath, "w")
    pickle.dump(videotimes(geocodes), out)
    out.flush()
    out.close()

def filetodto(track, videopath):
    dtos = []
    video = VideoFactory.createvideo(videopath)
    for (lat, lon, address, realtime, videotime) in pickle.load(track):
        dto = TracePointDTO(lat=lat, lon=lon, realtime=realtime, videotime=videotime, video=video, address=address)
        dtos.append(dto)
    return dtos

def resolveall():
    from geo.script.filldb import tracktovideo
    for trackpath in tracktovideo.keys():
        print "%s" % (trackpath)
        resolvefile(trackpath.replace(".geocode", ".gpx"), trackpath)

