"""MapEditor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from shapefiles.views import *
import tms.urls
urlpatterns = [
    url(r'^$', list_shapefiles),
    url(r'^import$', import_shapefile),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authentication/', include("MapEditor.authentication.urls")),
    url(r'^export/(?P<shapefile_id>\d+)', export_shapefile),
    url(r'^tms/', include("MapEditor.tms.urls")),
    url(r'^edit/(?P<shapefile_id>\d+$)', edit_shapefile),
    url(r'^find_feature$', find_feature),
    url(r'^edit_feature/(?P<shapefile_id>\d+)/(?P<feature_id>\d+)$', edit_feature),
    url(r'^edit_feature/(?P<shapefile_id>\d+)$', edit_feature),
    url(r'^delete_feature/(?P<shapefile_id>\d+)/(?P<feature_id>\d+)$', delete_feature),
    url(r'^delete/(?P<shapefile_id>\d+)$', delete_shapefile)
]
