'''
Created on Mar 18, 2012

@author: fredo
'''
from geo.web.forms.uploadform import UploadForm
from django.shortcuts import render_to_response
from settings import UPLOAD_PATH

import os
from geo.coordinate.gpx import GPX
from geo.script.gpxtogeocode import resolvefile, filetodto
from geo.video.ogg import Ogg

from django.views.generic.simple import direct_to_template
from tempfile import mkstemp
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from geo.map.map import Map
from geo.web.forms.trackform import TrackForm
from geo.web.message import failure
from geo.coordinate.jsonx import JSONX
import pprint
from geo.web.logger import getLogger
import tempfile

def index(request):
    logger = getLogger(__name__)
    if request.method == "POST":

        form = UploadForm(request.POST, request.FILES)
        messages = []
        errors = []

        if form.is_valid():
            logger.debug("upload form for mode %s is valid", form.cleaned_data["transportation_mode"])
            gpxfile = totemporaryfile(request.FILES["gps_trace"])
            videofile = totemporaryfile(request.FILES["video"])
            newvideopath = totemporaryfile().name

            gpx = GPX(gpxfile)

            #convert video, resolve points and add everything to the map
            if gpx.isvalid():
                logger.debug("gpx is valid")
                ogg = Ogg()
                oggvideopath = ogg.convert(videofile, newvideopath)
                logger.debug("video path: %s", oggvideopath)
                resolvefile(gpxfile.name, gpxfile.name)
                gpxfile.seek(0)
                dtos = filetodto(gpxfile, oggvideopath)
                map = Map.getinstance(form.cleaned_data["transportation_mode"])
                map.inserttracepoints(dtos)
                logger.debug("points added")
                os.remove(oggvideopath)
                os.remove(gpxfile.name)
                messages.append("Upload successful. The trace has been added to the map.")

            else:
                logger.debug("gpx not valid")
                errors.append("The supplied .gpx is not a valid GPX trace.")

            return direct_to_template(request, template="map.tpl", extra_context={"form":form, "messages":messages, "errors":errors})

    else:
        return direct_to_template(request, template="map.tpl", extra_context={"form":UploadForm()})


def totemporaryfile(upload=None, mode="rw"):
    if not upload:
        return open(mkstemp()[1], mode)
    logger = getLogger(__name__)
    logger.debug("upload file size: %d", upload.size)
    logger.debug("upload file name: %s", upload.name)
    path = tempfile.mkstemp()[1]

    file = open(path, "w+b")
    for chunk in upload.chunks():
        file.write(chunk)
    logger.debug("created temporary file %s" % (file.name))
    file.seek(0)
    return file



def track(request):
    logger = getLogger(__name__)
    if request.method == "POST":
        raise Http404
    trackform = TrackForm(request.GET)
    if not trackform.is_valid():
        return HttpResponseBadRequest(content=failure(trackform.errors), content_type="text/json")
    logger.debug("Request is valid. Get map %d", trackform.cleaned_data["mode"])
    map = Map.getinstance(trackform.cleaned_data["mode"])
    logger.debug("Map has %d mappoints and %d connections", len(map.mappoints), len(map.connections))

    json = JSONX()

    sourceid = trackform.cleaned_data["source"]
    targetid = trackform.cleaned_data["target"]

    if sourceid and targetid:
        logger.debug("Calculate shortest path")
        source = map.getmappoint(pointid=sourceid)
        target = map.getmappoint(pointid=targetid)
        if not source or not target:
            return HttpResponseBadRequest(content=failure("did not found source or target"), content_type="text/json")
        connectiontrack = map.getshortesttrack(source, target)
        print vars(connectiontrack)
        json.setconnectiontrack(connectiontrack, map)
        return HttpResponse(content=json.getjson(), content_type="text/json")

    else:
        print "Calculate whole track from %d mappoints with %d connections" % (len(map.mappoints), len(map.connections))
        pointtracks = map.getpointtracks()
        print "Got %d pointtracks" % len(pointtracks)
        json.setpointtracks(pointtracks)
        return HttpResponse(content=json.getjson(), content_type="text/json")

