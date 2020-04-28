# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from ..shared.models import ShapeFile
from django.shortcuts import redirect
from .forms import ImportShapefileForm
from django.http import Http404
from django.contrib.gis.geos import Point
from ..shared.utils import *
import shapeFilesIO
from ..shared.models import *
from django.contrib.auth.decorators import login_required
import os
from ..shared.decorators import *
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


@login_required
@require_GET
def list_shapefiles(request):
    shapefiles = ShapeFile.objects.all().filter(user_id=request.user.id).order_by("file_name")
    context = {
        "shapefiles": shapefiles,
    }
    return render(request, "list_shapefiles.html", context)


@ajax_login_required
@require_POST
def import_shapefile(request):
    shapefile = request.FILES['file']
    err_msg = shapeFilesIO.import_data(shapefile, request.user.id)
    if err_msg is None:
        data = {
            "ok": True,
            "errors": None
        }
    else:
        data = {
            "ok": False,
            "errors": [
                err_msg
            ]
        }
    return JsonResponse(data)


@login_required
def export_shapefile(request, shapefile_id):
    try:
        shapefile = ShapeFile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
        raise Http404("такой формат фигур не существует")

    return shapeFilesIO.export_data(shapefile)


@login_required
def edit_shapefile(request, shapefile_id):
    try:
        shapefile = ShapeFile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
        return HttpResponseNotFound()

    tms_url = "http://" + request.get_host() + "/tms"
    find_feature_url = "http://" + request.get_host() + "/editor/find_feature" + str(shapefile_id)
    add_feature_url = "http://" + request.get_host() + "/edit_feature/" + str(shapefile_id)
    return render(request, "select_feature.html", {
        "shapefile": shapefile,
        "tms_url": tms_url,
        "find_feature_url": find_feature_url,
        "add_feature_url": add_feature_url
    })


@login_required
def find_feature(request):
    try:
        shapefile_id = int(request.GET["shapefile_id"])
        latitude = float(request.GET["latitude"])
        longitude = float(request.GET["longitude"])
        shapefile = ShapeFile.objects.get(id=shapefile_id)
        pt = Point(longitude, latitude)
        radius = calc_search_radius(latitude, longitude, 1000)

        if shapefile.geom_type == "Point":
            query = Feature.objects.filter(geom_point__dwithin=(pt, radius))
        elif shapefile.geom_type in ['LineString', 'MultiLineString']:
            query = Feature.objects.filter(geom_multilinestring__dwithin=(pt, radius))
        elif shapefile.geom_type in ['Polygon', 'Multipolygon']:
            query = Feature.objects.filter(geom_multipolygon__dwithin=(pt, radius))
        elif shapefile.geom_type == 'MultiPoint':
            query = Feature.objects.filter(geom_multipoint__dwithin=(pt, radius))
        elif shapefile.geom_type == 'GeometryCollection':
            query = Feature.objects.filter(geom_geometrycollecion__dwithin=(pt, radius))
        else:
            print("Неподдерживаемая геометрия: ", shapefile.geom_type)
            return HttpResponse("")

        if query.count() != 1:
            return HttpResponse("")

        feature = query[0]
        return HttpResponse("/edit_feature" + "/" + str(shapefile_id) + "/" + str(feature.id))
    except:
        traceback.print_exc()
        return HttpResponse("")

    return HttpResponse("")


@login_required
def edit_feature(request, shapefile_id, feature_id=None):
    if request.method == "POST" and "delete" in request.POST:
        return HttpResponseRedirect("/delete_feature/" + shapefile_id + "/" + feature_id)
    try:
        shapefile = ShapeFile.objects.get(id=shapefile_id)
    except ShapeFile.DoesNotExist:
        return HttpResponseNotFound()

    if feature_id is None:
        feature = Feature(shapefile=shapefile)
    else:
        try:
            feature = Feature.objects.get(id=feature_id)
        except Feature.DoesNotExist:
            return HttpResponseNotFound()

    attributes = []
    for attr_value in feature.attributevalue_set.all():
        attributes.append([attr_value.attribute.name, attr_value.value])
    attributes.sort()

    geometry_field = calc_geometry_field(shapefile.geom_type)
    form_class = get_map_form(shapefile)

    if request.method == "GET":
        wkt = getattr(feature, geometry_field)
        form = form_class({'geometry': wkt})
        return render(request, "edit_feature.html",
                      {
                          "shapefile": shapefile,
                          "form": form,
                          "attributes": attributes
                      })
    elif request.method == "POST":
        form = form_class(request.POST)
        try:
            if form.is_valid():
                wkt = form.cleaned_data["geometry"]
                setattr(feature, geometry_field, wkt)
                feature.save()
                return HttpResponseRedirect("/edit/" + shapefile_id)
        except ValueError:
            pass

    return render(request, "edit_feature.html",
                  {
                      "shapefile": shapefile,
                      "form": form,
                      "attributes": attributes
                  })


@login_required
def delete_feature(request, shapefile_id, feature_id):
    try:
        feature = Feature.objects.get(id=feature_id)
    except Feature.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == "POST":
        if request.POST["confirm"] == "1":
            feature.delete()
        redirectUrl = request.build_absolute_uri('/') + "edit/" + shapefile_id
        return HttpResponseRedirect(redirectUrl)

    return render(request, "delete_feature.html")


@login_required
@require_POST
def delete_shapefile(request, shapefile_id):
    data = {

    }
    try:
        shapefile = ShapeFile.objects.get(id=shapefile_id)
        shapefile.delete()
        data["ok"] = True
        data["errors"] = []
    except ShapeFile.DoesNotExist:
        data["ok"] = True
        data["errors"] = ["Данного файла фигур не существует"]
    return JsonResponse(data)
