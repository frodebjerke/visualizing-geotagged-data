'''
Created on Mar 24, 2012

@author: fredo
'''
from geo.model.video import Video
from django.core.files import File
import uuid

class VideoFactory:

    @classmethod
    def createvideo(cls, path):

        video = Video(video=File(open(path, "rw")))
        video.save()
        return video
