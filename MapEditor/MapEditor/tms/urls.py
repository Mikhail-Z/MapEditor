from django.conf.urls import url
from MapEditor.tms.views import *
from views import *

urlpatterns = [
    url(r'^$', root),
    url(r'^(?P<version>[0-9\.]+)$', service),
    url(r'^(?P<version>[0-9\.]+)' +
        r'/(?P<shapefile_id>\d+)$', tileMap),
    url(r'^(?P<version>[0-9\.]+)' +
        r'/(?P<shapefile_id>\d+)' +
        r'/(?P<zoom>\d+)' +
        r'/(?P<x>\d+)/(?P<y>\d+)\.png$', tile)
]