'''
Created on Mar 20, 2012

Code based on http://the.taoofmac.com/space/blog/2005/10/11/2359

@author: fredo
'''
import sys, string
from xml.dom import minidom, Node
from geo.coordinate.parser import Parser
from geo.coordinate.exception import NoTrkTagException, NoTrkSegTagException, \
    NoTrkPtException
import re
from time import strptime, mktime
from decimal import Decimal
from datetime import datetime


class GPX(Parser):
    "GPX Parser for file-like objects"

    DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

    def isvalid(self):
        try:
            self.parse()
            for (lat, lon, time) in self.gettrackpoint():
                if (float(lat) == None) or (float(lon) == None) or (time == None):
                    return False
        except:
            return False

        return True


    def parse(self):

        try:
            doc = minidom.parse(self.file.name)
            doc.normalize()
        except Exception as e:
            raise e
        gpx = doc.documentElement
        tracks = gpx.getElementsByTagName('trk')
        if len(tracks) < 1:
            raise NoTrkTagException, "document does not has a track tag"
        self.track = tracks[0]

    def gettrackpoints(self):
        trackpoints = []
        for data in self.gettrackpoint():
            trackpoints.append(data)
        return trackpoints

    def gettrackpoint(self):
        self.parse()
        timeregex = re.compile("(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})")
        trksegs = self.track.getElementsByTagName('trkseg')

        if not trksegs:
            raise NoTrkSegTagException , "document does not has a track segment tag"

        for trkseg in trksegs:
            trkpts = trkseg.getElementsByTagName('trkpt')

            if not trkpts:
                raise NoTrkPtException, "document does not has a track point tag"

            for trkpt in trkpts:
                lat = Decimal(trkpt.getAttribute('lat'))
                lon = Decimal(trkpt.getAttribute('lon'))
                time = trkpt.getElementsByTagName('time')[0].firstChild.data
                match = timeregex.match(time)
                time = " ".join(match.groups())
                time = strptime(time, self.DATETIME_FMT)
                time = datetime.fromtimestamp(mktime(time))
                yield (lat, lon, time)

    def setpointtracks(self, mappointtracks):

        xml = minidom.Document()
        gpx = xml.createElement("gpx")
        gpx.setAttribute("version", "1.1")
        xml.appendChild(gpx)
        trk = xml.createElement("trk")
        gpx.appendChild(trk)
        for mappointtrack in mappointtracks:
            trkseq = xml.createElement("trkseg")
            trk.appendChild(trkseq)
            for mappoint in mappointtrack:
                trkpt = xml.createElement("trkpt")
                trkpt.setAttribute("lat", str(mappoint.lat))
                trkpt.setAttribute("lon", str(mappoint.lon))
                trkseq.appendChild(trkpt)
        self.xml = xml

    def setpointtrack(self, mappointtrack):
        return self.setpointtracks([mappointtrack])

    def write(self, file):
        file.write(self.xml.toprettyxml())
        file.close()
