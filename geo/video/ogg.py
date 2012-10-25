'''
Created on Mar 20, 2012

@author: fredo
'''

from geo.video.converter import Converter
import subprocess
import tempfile
import os

class Ogg(Converter):

    EXT = ".ogv"

    def convert(self, source, targetpath):
        targetpath = self.__normalizepath(targetpath)
        (temp, temppath) = self.__writetotemp(source)
        self.temppath = temppath
        args = self.__buildargs(temppath, targetpath)
        self.process = subprocess.Popen(args, shell=True)
        return targetpath

    def __buildargs(self, sourcepath, targetpath):
        return " ".join(["ffmpeg2theora", "-p %s" % self.profile, "-o %s" % targetpath, sourcepath])

    def __normalizepath(self, path):
        return os.path.join(
                            os.path.abspath(path),
                            os.path.splitext(path)[0] + self.EXT
                            )

    def __writetotemp(self, source):
        ext = os.path.splitext(source.name)[1]
        path = tempfile.mktemp() + ext
        temp = open(path, "wb")
        try:
            byte = source.read(1)
            while byte != "":
        # Do stuff with byte.
                temp.write(byte)
                byte = source.read(1)
        finally:
            temp.close()
            source.close()

        return (temp, path)

    def __del__(self):
        os.remove(self.temppath)
