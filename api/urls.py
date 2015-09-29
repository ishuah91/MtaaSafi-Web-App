from django.conf.urls import *
from tastypie.api import Api
from api.resources import AdministrativeUnitResource, AdministrativeUnitDetailResource, AdministrativeGroupResource, BaseSiteResource, UserResource, ShapeResource, PointResource, PolygonResource, MultiPolygonResource

v1_api = Api(api_name='v1')
v1_api.register(BaseSiteResource())
v1_api.register(UserResource())
v1_api.register(AdministrativeUnitResource())
v1_api.register(AdministrativeUnitDetailResource())
v1_api.register(AdministrativeGroupResource())
v1_api.register(ShapeResource())
v1_api.register(PointResource())
v1_api.register(PolygonResource())
v1_api.register(MultiPolygonResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)
