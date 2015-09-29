# From https://gist.github.com/samtux/29c8ee3bf36e12420348
import json
from tastypie.serializers import Serializer

class GeoJsonSerializer(Serializer):
    def to_geojson(self, data, options=None):
        """
        Given some Python data, produces GeoJSON output.
        """
        def _build_feature(obj):
            f = {
              "type": "Feature",
              "properties": {},
              "geometry": {}
            }
          
            def recurse(key, value):
                if key == 'id':
                    f[key] = value
                    return
                if key in ['coordinates', 'type']:
                    f['geometry'][key] = value
                if type(value) == type({}):
                    for k in value:
                        recurse(k, value[k])
                if key == "shapes" and type(value) == type([]) and len(value) > 0:
                    recurse("shape", value[0]["shape"])
                else:
                    f['properties'][key] = value
          
            for key, value in obj.iteritems():
                recurse(key, value)
            if not f['geometry'] == {}:
                return f
    
        def _build_feature_collection(objs, meta):
            fc = {
                "type": "FeatureCollection",
                "features": []
            }
            if(meta):
                fc["meta"] = meta
            for obj in objs:
                feat = _build_feature(obj)
                if feat:
                    fc['features'].append(feat)
            return fc
    
        options = options or {}
        data = self.to_simple(data, options)
        # print data
        if type(data) == type([]):
            data = data[0]
        meta = data.get('meta')
        
        if 'objects' in data:
            data = _build_feature_collection(data['objects'], meta)
        else:
            data = _build_feature(data)
        return json.dumps(data, sort_keys=True, ensure_ascii=False)
    
    def to_json(self, data, options=None):
        """
        Override to enable GeoJSON generation when the geojson option is passed.
        """
        options = options or {}
        return self.to_geojson(data, options)
