from TileCache.Cache import Cache
from TileCache.Service import Service
from TileCache.Layers.Mapnik import Mapnik
from models import TileCacheModel


class PostgresCache(Cache):
    def __init__(self, **kwargs):
        Cache.__init__(self, **kwargs)

    def get(self, tile_info):
        tile = TileCacheModel.objects.filter(shapefile_id=tile_info.shapefile_id, z=tile_info.z, x=tile_info.x, y=tile_info.y).first()
        if tile:
            return tile.data

        return None

    def set(self, tile_info, data):
        obj = TileCacheModel(shapefile_id=tile_info.shapefile_id, z=tile_info.z, x=tile_info.x, y=tile_info.y, data=data)
        obj.save()

        return data
