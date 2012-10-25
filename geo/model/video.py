'''
Created on Mar 22, 2012

@author: fredo
'''
from django.conf import settings
from django.db import models
from uuid import uuid4
import os

class Video(models.Model):
    video = models.FileField(upload_to=settings.UPLOAD_PATH)

    def getpath(self):
        path = self.video.path.replace(settings.MEDIA_ROOT, "")
        if path[0] == os.sep:
            path = path[1:]
        return os.sep + os.path.join("static", path)

    def __unicode__(self):
        return self.video.name

    class Meta:
        app_label = "geo"
