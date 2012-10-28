# Create your views here.


import os
from geo.io.gpx import GPX
from geo.script.gpxtogeocode import resolvefile, filetodto
from geo.video.ogg import Ogg

from django.views.generic.simple import direct_to_template
from tempfile import mkstemp
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from geo.routing.graph import Graph
from geo.forms import TrackForm,UploadForm

from geo.io.jsonx import JSONX
import tempfile
import logging

logger = logging.getLogger(__name__)

def index(request):
    
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

            #convert video, resolve points and add everything to the graph
            if gpx.isvalid():
                logger.debug("gpx is valid")
                ogg = Ogg()
                oggvideopath = ogg.convert(videofile, newvideopath)
                logger.debug("video path: %s", oggvideopath)
                resolvefile(gpxfile.name, gpxfile.name)
                gpxfile.seek(0)
                dtos = filetodto(gpxfile, oggvideopath)
                graph = Graph.getinstance(form.cleaned_data["transportation_mode"])
                graph.inserttracepoints(dtos)
                logger.debug("points added")
                os.remove(oggvideopath)
                os.remove(gpxfile.name)
                messages.append("Upload successful. The trace has been added to the graph.")

            else:
                logger.debug("gpx not valid")
                errors.append("The supplied .gpx is not a valid GPX trace.")

            return direct_to_template(request, template="index.html", extra_context={"form":form, "messages":messages, "errors":errors})

    else:
        return direct_to_template(request, template="index.html", extra_context={"form":UploadForm()})


def totemporaryfile(upload=None, mode="rw"):
    if not upload:
        return open(mkstemp()[1], mode)
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
    if request.method == "POST":
        raise Http404
    trackform = TrackForm(request.GET)
    if not trackform.is_valid():
        return HttpResponseBadRequest(content=failure(trackform.errors), content_type="text/json")
    logger.info("Request is valid. Get graph %d", trackform.cleaned_data["mode"])
    graph = Graph.getinstance(trackform.cleaned_data["mode"])
    logger.info("Graph has %d mappoints and %d connections", len(graph.mappoints), len(graph.connections))

    json = JSONX()

    sourceid = trackform.cleaned_data["source"]
    targetid = trackform.cleaned_data["target"]

    if sourceid and targetid:
        logger.info("Calculate shortest path")
        source = graph.getmappoint(pointid=sourceid)
        target = graph.getmappoint(pointid=targetid)
        if not source or not target:
            return HttpResponseBadRequest(content=failure("did not found source or target"), content_type="text/json")
        connectiontrack = graph.getshortesttrack(source, target)
        print vars(connectiontrack)
        json.setconnectiontrack(connectiontrack, graph)
        return HttpResponse(content=json.getjson(), content_type="text/json")

    else:
        logger.info("Calculate whole track from %d mappoints with %d connections" % (len(graph.mappoints), len(graph.connections)))
        pointtraces = graph.getpointtracks()
        logger.info("Got %d pointtraces" % len(pointtraces))
        json.pointtraces(pointtraces)
        return HttpResponse(content=json.getjson(), content_type="text/json")
    
def failure(error):
    return {"success" : False,
            "error" : str(error)}

def success():
    return {"success" : True}