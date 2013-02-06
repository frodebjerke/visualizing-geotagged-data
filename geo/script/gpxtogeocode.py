'''
Created on Mar 23, 2012

@author: fredo
'''

from geo.io.gpx import GPX
from geo.osm import OSM,calculate_distance
from geo.models import createvideo
from geo.routing.points import TracePointDTO
from geo.io.videotime import videotimes

import numpy as np
import os, pickle, logging, math, sys, glob
from numpy.lib.function_base import average
from decimal import Decimal

logger = logging.getLogger(__name__)

def resolvefile(inpath, outpath,mode):
    gpx = GPX(open(inpath, "r"))
    geocoder = OSM(mode)

    geocodes = []
    if not gpx.isvalid():
        raise RuntimeError, "gpx file is not valid"
    coordinates = gpx.gettrackpoints()
    geocodes = geocoder.reversegeocode(coordinates)
    
    
    if os.path.exists(outpath):
        path,ext = os.path.splitext(outpath)
        testpath = "%s.perfect%s" % (path,ext)
    
        if os.path.exists(testpath):
            logger.info("Test geocode file %s exists" % testpath)
            testgeocodes = pickle.load(open(testpath,"r"))
            if geocodes != testgeocodes:
                raise RuntimeError, "Geocodes are different"
        else:
            logger.info("Did not find test geocode file %s." % testpath)
            
    for index in range(len(coordinates)):
        if geocodes[index][2] != coordinates[index][2]:
            print "Times differ at %d." % index
            break 
    
    if len(geocodes) != len(coordinates):
        raise RuntimeError, "The same amount of geocoded coordinates should be present."
#    
#    for index in range(len(geocodes)):
#        
#    for (lat, lon) in gpx.gettrackpoint():
#        (lat_new, lon_new) = geocoder.reversegecode(lat=lat, lon=lon)
#        geocodes.append((lat_new,
#                         lon_new,
#                         time))
#        logger.debug("Processed %s, %s to %s,%s" % (lat, lon,lat_new,lon_new))
        
    out = open(outpath, "w")
    pickle.dump(videotimes(geocodes), out)
    pickle.dump(geocodes,out)
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
        logger.info("Resolving file %s in mode %d" % (trackpath, tracktovideo[trackpath][0]))
        resolvefile(trackpath.replace(".geocode", ".gpx"), trackpath, tracktovideo[trackpath][0])

def resolvetest():
    from django.conf import settings
    resolvedir(settings.EVALUATION_DIR)
    
        
def resolvedir(path):
    
    assert os.path.exists(path)
    path = os.path.abspath(path)
    
    for trace in glob.glob("%s/*.gpx" % path):
        logger.info("Resolving file %s." % trace)
        trace = os.path.join(path,trace)
        resolvefile(trace,trace.replace(".gpx",".geocode"),0)

def next_different(current, coordinates):
    for coordinate in coordinates:
        if coordinate[:2] != current[:2]:
            return coordinate
    return None


def calculateaverage():
    from geo.script.filldb import tracktovideo
    osm = OSM(1) 
    total_average = 0

    for trackpath in tracktovideo.keys():
        logger.info("Checking file %s in mode %d" % (trackpath, tracktovideo[trackpath][0]))
        path,ext = os.path.splitext(trackpath)
        gpxpath = path+".gpx"
        gpx = GPX(gpxpath)
        geocodes = pickle.load(open(trackpath,"r"))
        coordinates = gpx.gettrackpoints()
        total_distance = 0
        for index in range(len(coordinates)):
            current = geocodes[index]
            successor = next_different(current, geocodes[index:])
            tmp = geocodes[:index]
            tmp.reverse()
            predecessor = next_different(current,tmp)
            if index == 0:
                total_distance += distance_to_line(current, successor, coordinates[index])
            elif index == len(coordinates) - 1:
                total_distance += distance_to_line(predecessor,current , coordinates[index])
            else:
                if successor:
                    after = distance_to_line(current, successor, coordinates[index])
                else:
                    after = sys.maxint
                if predecessor:
                    before = distance_to_line(predecessor,current , coordinates[index])
                else:
                    before = sys.maxint
                total_distance += min(after,before)
#            total_distance += osm.calculate_distance(geocodes[index], coordinates[index])
        average = total_distance/len(geocodes)
        logger.info("Average is %f" % (average))
        total_average += average
    
    logger.info("Total average is %f." % (total_average/5))



R = 6367


def normalize(t):
    length =  math.sqrt((t[0] **2) + (t[1] **2) + (t[2]**2))
    return t/length

def deg_to_rad(x):
    return Decimal(x * Decimal(math.pi/180))

def rad_to_deg(x):
    return Decimal(x * Decimal(180/math.pi))

def from_cartesian(t):
    r = math.sqrt(t[0]**2 + t[1]**2 + t[2]**2);
    lat = rad_to_deg(Decimal(math.asin(t[2] / r)))
    lon = rad_to_deg(Decimal(math.atan2(t[1], t[0])))
    return (lat,lon)


def distance_to_line(a,b,c):
    a = np.array(to_cartesian(a))
    b = np.array(to_cartesian(b))
    c = np.array(to_cartesian(c))
    g = np.cross(a,b)
    f = np.cross(c,g)
    t = np.cross(g,f)
    t = normalize(t) * R #normalize
    return calculate_distance(from_cartesian(c),from_cartesian(t))
    

def to_cartesian(coordinate):
    lat = deg_to_rad(coordinate[0])
    lon = deg_to_rad(coordinate[1])
    x = R * math.cos(lat) * math.cos(lon)
    y = R * math.cos(lat) * math.sin(lon)
    z = R * math.sin(lat)
    return (x,y,z)

if __name__ == "__main__":
    resolvetest()