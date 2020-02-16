from TileCache.Cache import Cache
from TileCache.Service import Service
from TileCache.Layers.Mapnik import Mapnik

class TileCache()
    pass




class PostgresCache(Cache):
    def __init__(self, **kwargs):
        Cache.__init__(self, **kwargs)

    def get(self, tile):



