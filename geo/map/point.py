'''
Created on Mar 22, 2012

@author: fredo
'''

from django.db import models
from connectionmode import ConnectionMode

class Point(models.Model):
    
    #radius of what is considered near in different transportation modes
    IS_NEAR = ((ConnectionMode.WALK,30),
               (ConnectionMode.BIKE,60),
               (ConnectionMode.MOTOR_VEHICLE,200),
               (ConnectionMode.TRAIN,1000))

    class Meta:
        app_label ="geo"
        abstract = True