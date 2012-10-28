'''
Created on Mar 21, 2012

@author: fredo
'''

class OSMException(Exception): pass

class NoTrkTagException(Exception):
    pass

class NoTrkSegTagException(Exception):
    pass

class NoTrkPtException(Exception):
    pass

class InsertTracePointException(Exception):
    pass