'''
Created on Mar 20, 2012

@author: fredo
'''

from unittest import TestCase
from geo.coordinate.gpx import GPX
from settings import TEST_PATH
import os
from decimal import Decimal
from time import strftime
from geo.coordinate.exception import *

class GPXTest(TestCase):

    VALID_PATH = os.path.join(TEST_PATH, "valid.gpx")
    INVALID_TIME_PATH = os.path.join(TEST_PATH, "invalid_time.gpx")
    INVALID_COORD_PATH = os.path.join(TEST_PATH, "invalid_coord.gpx")
    NO_TRKPT_PATH = os.path.join(TEST_PATH, "no_trkpt.gpx")
    NO_TRKSEQ_PATH = os.path.join(TEST_PATH, "no_trkseq.gpx")
    NO_TRK_PATH = os.path.join(TEST_PATH, "no_trk.gpx")

    VALID_TRACKPOINTS = [
                        (Decimal("49.48483586311197"), Decimal("8.463313579559081"), "2012-03-07 11:38:07"),
                        (Decimal("49.484910964964385"), Decimal("8.463399410247558"), "2012-03-07 11:38:12"),
                        (Decimal("49.4849860668168"), Decimal("8.463485240936034"), "2012-03-07 11:38:39"),
                        (Decimal("49.48500752448892"), Decimal("8.463656902312987"), "2012-03-07 11:38:45"),
                        (Decimal("49.48499679565286"), Decimal("8.463742733001464"), "2012-03-07 11:38:49"),
                        (Decimal("49.48510408401346"), Decimal("8.463721275329345"), "2012-03-07 11:39:12"),
                        (Decimal("49.48521137237405"), Decimal("8.463699817657226"), "2012-03-07T11:39:16")]

    def setUp(self):
        self.valid = GPX(open(self.VALID_PATH, "r"))
        self.invalidcoord = GPX(open(self.INVALID_COORD_PATH, "r"))
        self.invalidtime = GPX(open(self.INVALID_TIME_PATH, "r"))
        self.notrk = GPX(open(self.NO_TRK_PATH, "r"))
        self.notrkpt = GPX(open(self.NO_TRKPT_PATH, "r"))
        self.notrkseq = GPX(open(self.NO_TRKSEQ_PATH, "r"))

    def testTrackpoint(self):
        gettrackpoints = self.valid.gettrackpoints()
        for index in range(len(gettrackpoints)):
            validtrackpoint = self.VALID_TRACKPOINTS[index]
            gettrackpoint = gettrackpoints[index]

            print "%s <--> %s" % (validtrackpoint[0], gettrackpoint[0])

            self.assertEqual(validtrackpoint[0], gettrackpoint[0], "lat should be equal")
            self.assertEqual(validtrackpoint[0], gettrackpoint[0], "lng should be equal")
            self.assertEqual(validtrackpoint[0], gettrackpoint[0], "date should be equal")


    def testValidate(self):
        self.assertTrue(self.valid.isvalid(), "Valid gpx file should validate to true")
        invalidmsg = "Invalid gpx file should validate to false"
        self.assertFalse(self.invalidcoord.isvalid(), invalidmsg)
        self.assertFalse(self.invalidtime.isvalid(), invalidmsg)
        self.assertFalse(self.notrk.isvalid(), invalidmsg)
        self.assertFalse(self.notrkpt.isvalid(), invalidmsg)
        self.assertFalse(self.notrkseq.isvalid(), invalidmsg)

    def testTrackpoints(self):
        self.assertRaises(NoTrkTagException, self.notrk.gettrackpoints)
        self.assertRaises(NoTrkSegTagException, self.notrkseq.gettrackpoints)
        self.assertRaises(NoTrkPtException, self.notrkpt.gettrackpoints)
