'''
Created on Mar 18, 2012

@author: fredo
'''

from django import forms
from geo.map.connectionmode import ConnectionMode
from dbus.connection import Connection


class UploadForm(forms.Form):
    TRANSPORTATION_MODE = (
                           (ConnectionMode.WALK, "Walk"),
                           (ConnectionMode.TRAIN, "Train"),
                           (ConnectionMode.BIKE, "Bike"),
                           (ConnectionMode.MOTOR_VEHICLE, "Motor Vehicle")
                           )
    video = forms.FileField()
    gps_trace = forms.FileField()
    transportation_mode = forms.ChoiceField(choices=TRANSPORTATION_MODE)


