# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth import get_user_model


class ShapeFile(models.Model):
    file_name = models.CharField(max_length=255)
    src_wkt = models.CharField(max_length=1024)
    geom_type = models.CharField(max_length=50)
    user = models.ForeignKey(get_user_model(), null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name


class Attribute(models.Model):
    shape_file = models.ForeignKey(ShapeFile)
    name = models.CharField(max_length=255)
    type = models.IntegerField()
    width = models.IntegerField()
    precision = models.IntegerField()

    def __str__(self):
        return self.name


class Feature(models.Model):
    shapefile = models.ForeignKey(ShapeFile)
    geom_point = models.PointField(srid=4326, blank=True, null=True)
    geom_multipoint = models.MultiPointField(srid=4326, blank=True, null=True)
    geom_multilinestring = models.MultiLineStringField(srid=4326, blank=True, null=True)
    geom_multipolygon = models.MultiPolygonField(srid=4326, blank=True, null=True)
    geom_geometrycollection = models.GeometryCollectionField(srid=4326, blank=True, null=True)
    objects = models.GeoManager()

    def __str__(self):
        return str(self.id)


class AttributeValue(models.Model):
    feature = models.ForeignKey(Feature)
    attribute = models.ForeignKey(Attribute)
    value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.value