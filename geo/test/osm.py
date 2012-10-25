# coding=UTF-8
'''
Created on Mar 21, 2012

@author: fredo
'''

from unittest import TestCase
from geo.osm import OSM
from decimal import Decimal


class OSMTest(TestCase):
    
    ZOOM_18 = (
                 (Decimal("49.484921693800445"),Decimal("8.463377952575438"),Decimal("49.48510445"),Decimal("8.46306305"),"Landgericht Mannheim, Marktstraße, Innenstadt, Mannheim, Regierungsbezirk Karlsruhe, Baden-Württemberg, 68159, Federal Republic of Germany (land mass)"),
                 (Decimal("52.5487429714954"),Decimal("-1.81602098644987"),Decimal("52.5487800167257"),Decimal("-1.81626922829143"),"137, Pilkington Avenue, Castle Vale, Birmingham, West Midlands, England, B72 1LH, United Kingdom"),)
    ZOOM_15 = (
               (Decimal("52.5487429714954"),Decimal("-1.81602098644987"),Decimal("52.5212593"),Decimal("-1.7845494"),"Castle Vale, Birmingham, West Midlands, England, United Kingdom"),)
               
               
    def setUp(self):
        self.osm = OSM()
        
    def testReversegeocode18(self):
        self.reversegeocode(self.ZOOM_18,18)
            
    def testReversegeocode15(self):
        self.reversegeocode(self.ZOOM_15, 15)
        
    def reversegeocode(self,data,zoom):
        for lat,lon,exlat,exlon,exadress in data:
            (relat,relon,readress) = self.osm.reversegecode(lat, lon, zoom)
            self.assertEquals(relat,exlat)
            self.assertEquals(relon,exlon)
            self.assertEquals(readress,exadress)
            