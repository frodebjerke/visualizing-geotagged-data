# Create your models here.

from django.db import models
from  django.conf import settings
from django.core.files import File

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

#    class Meta:
#        app_label = "geo"
        

def createvideo(path):

    video = Video(video=File(open(path, "rw")))
    video.save()
    return video

