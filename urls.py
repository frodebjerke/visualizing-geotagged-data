from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
# from geo.web.forms.uploadform import UploadForm
admin.autodiscover()


from geo.views import index, track
from info.views import info, wikipedia


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
         (r'^$', index),
         (r'^track/$', track),
         (r'^info/$', info),
         (r'^info/wikipedia/(?P<title>[^/]+)/$', wikipedia),
         (r'^info/wikipedia/(?P<title>[^/]+)/(?P<language>[a-z]{2})/$', wikipedia),
    # url(r'^geotag/', include('geotag.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)

