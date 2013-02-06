'''
Created on Oct 28, 2012

@author: fredo
'''

import subprocess as sub
import sys

SYNCDB = "python manage.py syncdb"
DBSHELL = "python manage.py dbshell"
SHELL = "python manage.py shell"


def resetdb():
    p = sub.Popen(DBSHELL,shell = True, stdout = sub.PIPE, stdin = sub.PIPE)
    p.stdin.write("\i clear.sql\n")
    p.communicate("\q")
    print sub.check_output(SYNCDB, shell = True)

def insert():
    p = sub.Popen(SHELL,shell = True, stdout = sub.PIPE, stdin = sub.PIPE)
    p.stdin.write("from geo.script.filldb import insertevaluation,insertall\n")
    #p.communicate("from geo.script.filldb import insertall\n")
    #p.communicate("insertall()")
    p.communicate("insertevaluation()")
    
    
if __name__=="__main__":
    resetdb()
    insert()