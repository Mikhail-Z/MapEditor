# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib.gis import admin
from models import *

admin.site.register(ShapeFile, admin.ModelAdmin)
admin.site.register(Attribute, admin.GeoModelAdmin)
admin.site.register(Feature, admin.ModelAdmin)
admin.site.register(AttributeValue, admin.ModelAdmin)