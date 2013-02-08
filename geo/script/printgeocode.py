'''
Created on Feb 8, 2013

@author: fredo
'''

from gpxtogeocode import filetodto
from geo.test.map import VIDEO_PATH
from filldb import tracktovideo

def getdtos(path):
    return filetodto(path, VIDEO_PATH)
    
        
        
if __name__ == "__main__":
    dtos1 = getdtos(open(tracktovideo[1][0], "r"))
#    print "-" * 50
    dtos2 = getdtos(open(tracktovideo[2][0], "r"))
#    dtos2.reverse()
    for i in range(max(len(dtos1), len(dtos2))):
        try:
            dto1 = dtos1[i]
        except IndexError, e:
            dto1 = "N.A"
        try:
            dto2 = dtos2[i]
        except IndexError, e:
            dto2 = "N.A"
            
        print "%s\t%s" % (dto1, dto2)