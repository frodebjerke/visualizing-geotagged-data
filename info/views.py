# Create your views here.


from django.http import HttpResponse, HttpResponseBadRequest

def info(request):
    
    if request.method == "POST":
        try:
            lat = int(request.POST["lat"])
            lon = int(request.POST["lon"])
            return HttpResponse(content = "some information", content_type = "text/json")
        except Exception, e:
            return HttpResponse(content = "Something went wrong", content_type = "text/json")
    else:
        return HttpResponseBadRequest()
    
    