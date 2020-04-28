# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import tempfile
import traceback
import zipfile

from django.contrib.gis.geos.geometry import GEOSGeometry
from django.http import FileResponse
from osgeo import osr

from ..shared.models import *
from ..shared.utils import *


def import_data(shapefile, user_id):

    # Extract the uploaded shapefile.

    fd,fname = tempfile.mkstemp(suffix="zip")
    os.close(fd)

    f = open(fname, "wb")
    for chunk in shapefile.chunks():
        f.write(chunk)
    f.close()

    if not zipfile.is_zipfile(fname):
        os.remove(fname)
        return "Not a valid zip archive."

    zip = zipfile.ZipFile(fname)

    required_suffixes = [".shp", ".shx", ".dbf", ".prj"]
    has_suffix = {}
    for suffix in required_suffixes:
        has_suffix[suffix] = False

    for info in zip.infolist():
        suffix = os.path.splitext(info.filename)[1].lower()
        if suffix in required_suffixes:
            has_suffix[suffix] = True

    for suffix in required_suffixes:
        if not has_suffix[suffix]:
            zip.close()
            os.remove(fname)
            return "Archive missing required " + suffix + " file."

    shapefile_name = None
    dir_name = tempfile.mkdtemp()
    for info in zip.infolist():
        if info.filename.endswith(".shp"):
            shapefile_name = info.filename

        dst_file = os.path.join(dir_name, info.filename)
        f = open(dst_file, "wb")
        f.write(zip.read(info.filename))
        f.close()
    zip.close()

    # Open the shapefile.

    try:
        datasource = ogr.Open(os.path.join(dir_name, shapefile_name))
        layer      = datasource.GetLayer(0)
        shapefile_ok = True
    except:
        traceback.print_exc()
        shapefile_ok = False

    if not shapefile_ok:
        os.remove(fname)
        shutil.rmtree(dir_name)
        return "Not a valid shapefile."

    # Save Shapefile object to database.

    src_spatial_ref = layer.GetSpatialRef()
    geom_type = layer.GetLayerDefn().GetGeomType()
    geom_name = ogr.GeometryTypeToName(geom_type)
    geom_name = geom_name.replace(" ", "")
    shapefile = ShapeFile(file_name=shapefile_name,
                          src_wkt=src_spatial_ref.ExportToWkt(),
                          geom_type=geom_name,
                          user_id=user_id)
    shapefile.save()

    # Define the shapefile's attributes.

    attributes = []
    layer_def = layer.GetLayerDefn()
    for i in range(layer_def.GetFieldCount()):
        field_def = layer_def.GetFieldDefn(i)
        attr = Attribute(shape_file=shapefile,
                         name=field_def.GetName(),
                         type=field_def.GetType(),
                         width=field_def.GetWidth(),
                         precision=field_def.GetPrecision())
        attr.save()
        attributes.append(attr)

    # Save the Shapefile's features and attributes to disk.

    dst_spatial_ref = osr.SpatialReference()
    dst_spatial_ref.ImportFromEPSG(4326)

    coord_transform = osr.CoordinateTransformation(
                                      src_spatial_ref,
                                      dst_spatial_ref)

    for i in range(layer.GetFeatureCount()):
        src_feature = layer.GetFeature(i)
        src_geometry = src_feature.GetGeometryRef()
        src_geometry.Transform(coord_transform)
        geometry = GEOSGeometry(src_geometry.ExportToWkt())
        geometry = wrap_geos_geometry(geometry)

        geom_field = calc_geometry_field(geom_name)

        fields = {}
        fields['shapefile'] = shapefile
        fields[geom_field] = geometry

        feature = Feature(**fields)
        feature.save()

        for attr in attributes:
            success,result = get_ogr_feature_attribute(
                                      attr, src_feature)
            if not success:
                os.remove(fname)
                shutil.rmtree(dir_name)
                shapefile.delete()
                return result

            attr_value = AttributeValue(feature=feature,
                                        attribute=attr,
                                        value=result)
            attr_value.save()

    os.remove(fname)
    shutil.rmtree(dir_name)
    return None

#############################################################################

def export_data(shapefile):

    # Create the shapefile.

    dst_dir = tempfile.mkdtemp()
    dst_file = os.path.join(dst_dir, shapefile.file_name)

    dst_spatial_ref = osr.SpatialReference()
    dst_spatial_ref.ImportFromWkt(shapefile.src_wkt)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.CreateDataSource(dst_file)

    layer_name = shapefile.file_name.encode("utf-8")
    layer = datasource.CreateLayer(layer_name,
                                   dst_spatial_ref)

    # Define the shapefile's attributes.

    for attr in shapefile.attribute_set.all():
        print("attribute: ", attr)
        attribute_name = attr.name.encode("utf-8")
        field = ogr.FieldDefn(attribute_name, attr.type)
        print("field: ", field)
        field.SetWidth(attr.width)
        field.SetPrecision(attr.precision)
        layer.CreateField(field)

    # Create our coordinate transformation.

    src_spatial_ref = osr.SpatialReference()
    src_spatial_ref.ImportFromEPSG(4326)

    coord_transform = osr.CoordinateTransformation(
                          src_spatial_ref, dst_spatial_ref)

    # Calculate which geometry field holds the shapefile's geometry.

    geom_field = calc_geometry_field(shapefile.geom_type)

    # Export the shapefile's features.

    for feature in shapefile.feature_set.all():
        geometry = getattr(feature, geom_field)
        geometry = unwrap_geos_geometry(geometry)

        dst_geometry = ogr.CreateGeometryFromWkt(geometry.wkt)
        dst_geometry.Transform(coord_transform)

        dst_feature = ogr.Feature(layer.GetLayerDefn())
        dst_feature.SetGeometry(dst_geometry)

        for attr_value in feature.attributevalue_set.all():
            set_ogr_feature_attribute(
                    attr_value.attribute,
                    attr_value.value,
                    dst_feature)

        layer.CreateFeature(dst_feature)

    layer      = None
    datasource = None

    # Compress the shapefile as a ZIP archive.

    temp = tempfile.TemporaryFile()
    zip = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)

    shapefile_name = os.path.splitext(shapefile.file_name)[0]

    for fName in os.listdir(dst_dir):
        zip.write(os.path.join(dst_dir, fName), fName)

    zip.close()
    shutil.rmtree(dst_dir)

    # Return the ZIP archive back to the caller.

    temp.flush()
    temp.seek(0)

    response = FileResponse(temp)
    response['Content-type'] = "application/zip"
    response['Content-Disposition'] = \
        "attachment; filename=" + shapefile_name + ".zip"
    return response

