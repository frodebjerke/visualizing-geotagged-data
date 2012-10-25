'''
Created on Mar 30, 2012

@author: fredo
'''

def failure(error):
    return {"success" : False,
            "error" : str(error)}

def success():
    return {"success" : True}
