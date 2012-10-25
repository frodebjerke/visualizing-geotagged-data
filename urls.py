from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
from geo.web.forms.uploadform import UploadForm
admin.autodiscover()


from geo.web.handler.handler import index, track


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('de.uni.mannnheim.informatik.geo.video',
    # Examples:
         url(r'^$', index),
         (r'track/$', track),
    # url(r'^geotag/', include('geotag.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)

