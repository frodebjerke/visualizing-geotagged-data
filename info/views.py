# Create your views here.

from django.http import HttpResponse, HttpResponseBadRequest

import wiki2plain
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
def wikipedia(request, title):
    wikipage = Page(Wiki("http://en.wikipedia.org/w/api.php"), title = title)
    return HttpResponse(wiki2plain.Wiki2Plain(wikipage.getWikiText()).text)

