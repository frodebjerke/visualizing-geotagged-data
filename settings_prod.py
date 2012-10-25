'''
Created on Jun 15, 2012

@author: fredo
'''

from settings import *

DEBUG = False
TEMPLATE_DEBUG = False

temp_app = tuple()

for app in INSTALLED_APPS:
    if not app == "django.contrib.admin":
        temp_app += (app,)

INSTALLED_APPS = temp_app
