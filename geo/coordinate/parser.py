'''
Created on Mar 20, 2012

@author: fredo
'''

import os

class Parser():
    "Parser for file-like objects. To read from file hand it over in the constructor. To write hand it over to the write function."

    def __init__(self, file=None):
        "Use file if you want to read from file."
        self.file = file

    def parse(self):
        "Builds the DOM."
        pass

    def isvalid(self):
        pass

    def gettrackpoint(self):
        pass

    def gettrackpoints(self):
        pass

    def setpointtracks(self, mappoints):
        pass

    def write(self, file):
        pass
