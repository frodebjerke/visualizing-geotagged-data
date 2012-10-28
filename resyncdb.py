'''
Created on Oct 28, 2012

@author: fredo
'''

import subprocess as sub
import sys

SYNCDB = "python manage.py syncdb"
DBSHELL = "python manage.py dbshell"
SHELL = "python manage.py shell"

p = sub.Popen(DBSHELL,shell = True, stdout = sub.PIPE, stdin = sub.PIPE)
p.stdin.write("django\n")
p.stdin.write("\i clear.sql\n")
p.communicate("\q")

print sub.check_output(SYNCDB,shell = True)

p = sub.Popen(SHELL,shell = True, stdout = sub.PIPE, stdin = sub.PIPE)
p.stdin.write("from geo.script.filldb import insertall\n")
#p.communicate("from geo.script.filldb import insertall\n")
p.communicate("insertall()")