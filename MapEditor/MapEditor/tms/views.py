# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import traceback
from ..shared.models import ShapeFile
from django.http import Http404
import math
import mapnik
from .. import settings
from ..shared import utils

MAX_ZOOM_LEVEL = 10
TILE_WIDTH = 256
TILE_HEIGHT = 256

def root(request):
    try:
        baseUrl = request.build_absolute_uri()
        xml = []
        xml.append('<xml version="1.0" encoding="utf-8" ?>')
        xml.append('<Services>')
        xml.append('<TileMapService title="Служба TMS приложения MapEditor" version="1.0" href="' + baseUrl + '/1.0"/>')
        xml.append('</Services>')
        response = "\n".join(xml)
        return HttpResponse(response, "text/xml")
    except:
        traceback.print_exc()
        return HttpResponse("Ошибка")


def service(request, version):
    try:
        if version != "1.0":
            return Http404

        baseUrl = request.build_absolute_uri()
        xml = []
        xml.append('<xml version="1.0" encoding="utf-8" ?>')
        xml.append('<TileMapService version="1.0" href="' + baseUrl + '/>')
        xml.append('<Title>' + 'Служба TMS приложения MapEditor' + '</Title>')
        xml.append('<Abstract></Abstract>')
        xml.append('<TileMaps>')
        for shapefile in ShapeFile.objects.all():
            id = int(shapefile.id)
            xml.append('<TileMap title="' + shapefile.file_name + '"')
            xml.append('srs="EPSG:4326"')
            xml.append('href="' + baseUrl + '/' + str(id) + '"/>')
        xml.append('</TileMaps>')
        xml.append('<TileMapService')
        response = "\n".join(xml)
        return HttpResponse(response, "text/xml")
    except:
        traceback.print_exc()
        return Http404


def tileMap(request, version, shapefile_id):
    try:
        if version != "1.0":
            return Http404
        shapefile = ShapeFile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
        raise Http404

    try:
        baseUrl = request.build_absolute_uri()
        xml = []
        xml.append('<xml version="1.0" encoding="utf-8" ?>')
        xml.append('TileMap version="1.0" ' + 'tilemapservice="' + baseUrl + '">')
        xml.append('<Title>' + shapefile.file_name + '</Title>')
        xml.append('<Abstract></Abstract>')
        xml.append('<SRS>EPSG:4326</SRS>')
        xml.append('<BoundingBox minx="-180" miny="-90" maxx="180" maxy="90"/>')
        xml.append('<Origin x="-180" y="-90"/>')
        xml.append('<TileFormat width="' + str(TILE_WIDTH) + ' "/>')
        xml.append('<TileFormat width="' + str(TILE_WIDTH) + ' "mime-type="image/png" extension="png"/>')
        xml.append('<TileSets profile="global-geodetic"/>')
        for zoomLevel in range(0, MAX_ZOOM_LEVEL + 1):
            href=baseUrl + "/{}".format(zoomLevel)
            unitsPerPixel = '{}'.format(_unitsPerPixel(zoomLevel))
            order = '{}'.format(zoomLevel)
            xml.append('<TileSet href="' + href + '" unitsPerPixel="' + unitsPerPixel +
            'order="' + order + '"/>')
        xml.append('</TileSets>')
        xml.append('</TileMap>')
        response = "\n".join(xml)
        return HttpResponse(response, content_type="text/html")
    except:
        traceback.print_exc()
        return HttpResponse("Ошибка")

'''
def tile(request, version, shapefile_id, zoom, x, y):
    try:
        if version != "1.0":
            raise Http404
        try:
            shapefile = ShapeFile.objects.get(id=shapefile_id)
        except ShapeFile.DoesNotExist:
            raise Http404
        zoom = int(zoom)
        x = int(x)
        y = int(y)

        if zoom < 0 or zoom > MAX_ZOOM_LEVEL:
            raise Http404
        xEntent = _unitsPerPixel(zoom) * TILE_WIDTH
        yEntent = _unitsPerPixel(zoom) * TILE_HEIGHT

        minLong = x * xEntent - 180.0
        minLat = y * yEntent - 90.0
        maxLong = x * xEntent + 180.0
        maxLat = y * yEntent + 90.0

        if minLat < -90 or maxLat > 90 or minLong < -180.0 or maxLong > 180.0:
            raise Http404

        map = mapnik.Map(TILE_WIDTH, TILE_HEIGHT, "+proj=longlat +datum=WGS84".encode("utf-8"))
        map.background = mapnik.Color("#7371ad".encode("utf-8"))
        dbSettings = settings.DATABASES["default".encode("utf-8")]

        datasource = mapnik.PostGIS(user=dbSettings["USER"],
                                    password=dbSettings["PASSWORD"],
                                    dbname=dbSettings["NAME"],
                                    host=dbSettings["HOST"],
                                    table="tms_basemap".encode("utf-8"),
                                    srid=4326,
                                    geometry_field="geometry".encode("utf-8"),
                                    geometry_table="tms_basemap".encode("utf-8"))

        baseLayer = mapnik.Layer("baseLayer".encode("utf-8"))
        baseLayer.datasource = datasource
        baseLayer.styles.append("baseLayerStyle".encode("utf-8"))

        rule = mapnik.Rule()

        p = mapnik.PolygonSymbolizer()
        c = mapnik.Color("#b5d19c".encode("utf-8"))
        p.fill("#b5d19c".encode("utf-8"))
        rule.symbols.append(mapnik.LineSymbolizer(mapnik.Color("#404040".encode("utf-8")), 0.2))
        rule.symbols.append(p)
        style = mapnik.Style()
        style.rules.append(rule)

        map.append_styles("baseLayerStyle", style)
        map.layers.append(baseLayer)

        geometry_field = utils.calc_geometry_field(shapefile.geom_type)
        query = '(select ' + geometry_field + \
        ' from "shared_feature" where shapefile_id = ' + str(shapefile_id) + ') as geom'.encode("utf-8")

        datasource = mapnik.PostGIS(user=dbSettings["USER"],
                                    password=dbSettings["PASSWORD"],
                                    dbname=dbSettings["NAME"],
                                    table="tms_basemap".encode("utf-8"),
                                    srid=4326,
                                    geometry_field="geometry_field".encode("utf-8"),
                                    geometry_table="shared_feature".encode("utf-8"))

        featureLayer = mapnik.Layer("featureLayer".encode("utf-8"))
        featureLayer.datasource = datasource
        featureLayer.styles.append("featureLayerStyle".encode("utf-8"))

        rule = mapnik.Rule()
        if shapefile.geom_type in ["Point", "MultiPoint"]:
            rule.symbols.append(mapnik.PointSymbolizer())
        elif shapefile in ["LineString", "MultiLineString"]:
            rule.symbols_append(mapnik.LineSymbolizer(mapnik.Color("#000000", 0.5)))
        elif shapefile.geom_type in ["Polygon", "MultiLinePolygon"]:
            rule.symbols.append(mapnik.PolygonSymbolizer(mapnik.Color("##f7edee")))
            rule.symbols.append(mapnik.MultiLineSymbolizer(mapnik.Color("#000000", 0.5)))

        style = mapnik.Style()
        style.rules.append(rule)
        map.append_style("featureLevelStyle", style)
        map.layers.append(featureLayer)
        map.zoom_to_box(mapnik.Box2d(minLong, minLat, maxLong, maxLat))
        image = mapnik.Image(TILE_WIDTH, TILE_HEIGHT)
        mapnik.render(map, image)
        imageData = image.tostring("png")

        return HttpResponse(imageData, content_type="image/png")
    except:
        traceback.print_exc()
        return HttpResponse("Ошибка")
'''

def tile(request, version, shapefile_id, zoom, x, y):
    print(x, y)
    try:
        if version != "1.0":
            raise Http404
        try:
            shapefile = ShapeFile.objects.get(id=shapefile_id)
        except ShapeFile.DoesNotExist:
            raise Http404
        zoom = int(zoom)
        x = int(x)
        y = int(y)

        if zoom < 0 or zoom > MAX_ZOOM_LEVEL:
            raise Http404
        xEntent = _unitsPerPixel(zoom) * TILE_WIDTH
        yEntent = _unitsPerPixel(zoom) * TILE_HEIGHT

        minLong = x * xEntent - 180.0
        minLat = y * yEntent - 90.0
        maxLong = minLong + xEntent
        maxLat = minLat + yEntent

        if minLat < -90 or maxLat > 90 or minLong < -180.0 or maxLong > 180.0:
            raise Http404
        dbSettings = settings.DATABASES["default".encode("utf-8")]
        user = dbSettings["USER"]
        password = dbSettings["PASSWORD"]
        dbname = dbSettings["NAME"]
        geometry_field = utils.calc_geometry_field(shapefile.geom_type)
        query = '(select ' + geometry_field + \
                ' from "shared_feature" where shapefile_id = ' + str(shapefile_id) + ') as geom'.encode("utf-8")

        if shapefile.geom_type in ["Point", "MultiPoint"]:
            symbolizer = "<PointSymbolizer>"
        elif shapefile in ["LineString", "MultiLineString"]:
            symbolizer = '<LineSymbolizer strike="#000000" stroke=width="0.5"/>'
        elif shapefile.geom_type in ["Polygon", "MultiPolygon"]:
            symbolizer = '<PolygonSymbolizer fill="#f7edee"/>' +\
                '<LineSymbolizer stroke="#000000" stroke-width="0.5"/>'
        map_string = '''<?xml version="1.0" encoding="utf-8"?>
        <Map background-color="#7391ad" srs="+proj=longlat +datum=WGS84">
            <!--<FontSet name="bold-fonts">
                <Font face-name="DejaVu Sans"/>
            </FontSet>-->
            <Style name="baseLayerStyle">
                <Rule>
                    <PolygonSymbolizer fill="#b5d19c"/>
                    <LineSymbolizer stroke="#404040" stroke-width="0.2"/>
                </Rule>
            </Style>
            <Style name="featureLayerStyle">
                <Rule>
                    <!--(Symbolizers)-->
                </Rule>
            </Style>
            <Layer name="baseLayer">
                <StyleName>baseLayerStyle</StyleName>
                <Datasource>
                    <Parameter name="type">postgis</Parameter>
                    <Parameter name="dbname">(Dbname)</Parameter>
                    <Parameter name="table">tms_basemap</Parameter>
                    <Parameter name="user">(User)</Parameter>
                    <Parameter name="password">(Password)</Parameter>
                    <Parameter name="geometry_field">geometry</Parameter>
                    <Parameter name="geometry_table">tms_basemap</Parameter>
                    <Parameter name="srid">4326</Parameter>
                </Datasource>
            </Layer>
            <Layer name="featureLayer">
                <StyleName>featureLayerStyle</StyleName>
                <Datasource>
                    <Parameter name="type">postgis</Parameter>
                    <Parameter name="dbname">(Dbname)</Parameter>
                    <Parameter name="table">(Query)</Parameter>
                    <Parameter name="user">(User)</Parameter>
                    <Parameter name="password">(Password)</Parameter>
                    <Parameter name="geometry_field">(Geometry_field)</Parameter>
                    <Parameter name="geometry_table">shared_feature</Parameter>
                    <Parameter name="srid">4326</Parameter>
                </Datasource>
            </Layer>
        </Map>'''

        map_string = map_string.replace("<!--(Symbolizers)-->", symbolizer)\
            .replace("(Dbname)", dbname)\
            .replace("(User)", user)\
            .replace("(Password)", password)\
            .replace("(Geometry_field)", geometry_field)\
            .replace("(Query)", query)

        gmap = mapnik.Map(TILE_WIDTH, TILE_HEIGHT)
        mapnik.load_map_from_string(gmap, map_string.encode("utf-8"))
        gmap.zoom_to_box(mapnik.Box2d(minLong, minLat, maxLong, maxLat))
        image = mapnik.Image(TILE_WIDTH, TILE_HEIGHT)
        mapnik.render(gmap, image)
        imageData = image.tostring('png'.encode("utf-8"))
        return HttpResponse(imageData, content_type="image/png")
    except:
        traceback.print_exc()
        return HttpResponse("Ошибка")


def _unitsPerPixel(zoomLevel):
    return 0.703125/math.pow(2, zoomLevel)