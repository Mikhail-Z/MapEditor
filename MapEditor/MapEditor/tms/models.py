# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models
from ..shared.models import ShapeFile

class BaseMap(models.Model):
    name = models.CharField(max_length=50)
    geometry = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __str__(self):
        return self.name


class TileCacheModel(models.Model):
    z = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()
    shapefile = models.ForeignKey(ShapeFile, null=True)
    data = models.BinaryField()

    class Meta:
        managed = True
        db_table = 'tile_cache'
        unique_together = ['z', 'x', 'y', 'shapefile']
        index_together = ['z', 'x', 'y', 'shapefile']
