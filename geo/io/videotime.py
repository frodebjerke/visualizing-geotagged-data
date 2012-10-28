'''
Created on Mar 24, 2012

@author: fredo
'''

def videotimes(geocodes):
    videotimes = []
    start = None
    for (lat,lon,realtime) in geocodes:
        if not start:
            start = realtime
            videotime = 0
        else:
            td = realtime-start
            videotime = td.seconds
        videotimes.append((lat,lon,realtime,videotime))
    return videotimes
            