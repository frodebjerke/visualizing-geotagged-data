# Create your views here.

from django.http import HttpResponse, HttpResponseBadRequest

import wiki2plain
import re

from wikitools import Wiki, Page

def info(request):
    
    if request.method == "POST":
        try:
            # you might want to use Number to prevent having a million zeros
            lat = float(request.POST["lat"])
            lon = float(request.POST["lon"])
            return HttpResponse(content = "some information", content_type = "text/json")
        except Exception, e:
            return HttpResponse(content = "Something went wrong", content_type = "text/json")
    else:
        return HttpResponseBadRequest()

"""
Returns the plain text of wikipedia article with given title
@author Jan Vorcak <janvor@ifi.uio.no>
"""
def wikipedia(request, title, language="en"):

    if request.is_ajax():
        wikipage = Page(Wiki("http://"+language+".wikipedia.org/w/api.php"), title = title)
        text = wiki2plain.Wiki2Plain(wikipage.getWikiText()).text
        text = re.sub(r"===([^=]*)===", r"<h2>\1</h2>", text)
        text = re.sub(r"==([^=]*)==", r"<h3>\1</h3>", text)
        return HttpResponse(text)
    else:
        return HttpResponse("")

