'''
Created on Mar 30, 2012

@author: fredo
'''
from django import forms

class TrackForm(forms.Form):
    source = forms.IntegerField(required=False)
    target = forms.IntegerField(required=False)
    mode = forms.IntegerField()
