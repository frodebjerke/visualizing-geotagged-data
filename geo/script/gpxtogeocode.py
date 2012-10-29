'''
Created on Mar 23, 2012

@author: fredo
'''

from geo.io.gpx import GPX
from geo.osm import OSM
from geo.models import createvideo
from geo.routing.points import TracePointDTO
from geo.io.videotime import videotimes

import os
import pickle
import logging

logger = logging.getLogger(__name__)

def resolvefile(inpath, outpath,mode):
    gpx = GPX(open(inpath, "r"))
    geocoder = OSM(mode)

    geocodes = []
    if not gpx.isvalid():
        raise RuntimeError, "gpx file is not valid"
    for (lat, lon, time) in gpx.gettrackpoint():
        (lat_new, lon_new) = geocoder.reversegecode(lat=lat, lon=lon)
        geocodes.append((lat_new,
                         lon_new,
                         time))
        logger.debug("Processed %s, %s to %s,%s" % (lat, lon,lat_new,lon_new))
    out = open(outpath, "w")
    pickle.dump(videotimes(geocodes), out)
    out.flush()
    out.close()

def filetodto(track, videopath):
    dtos = []
    video = createvideo(videopath)
    logger.info("Reading from %s..." % track)
    for (lat, lon, realtime, videotime) in pickle.load(track):
        dto = TracePointDTO(lat=lat, lon=lon, realtime=realtime, videotime=videotime, video=video)
        dtos.append(dto)
    return dtos

def resolveall():
    from geo.script.filldb import tracktovideo 
    for trackpath in tracktovideo.keys():
        logger.info("Resolving file %s" % (trackpath))
        resolvefile(trackpath.replace(".geocode", ".gpx"), trackpath, tracktovideo[trackpath][0])

if __name__ == "__main__":
    resolveall()