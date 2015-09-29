import json
from topojson import topojson
from geojson_serializer import *
from tastypie import fields
from tastypie.resources import ALL
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.authorization import Authorization
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.db.models import Count
from django.contrib.gis import geos
from django.contrib.gis.measure import D
from tastypie.contrib.gis.resources import ModelResource
from django.contrib.auth.models import User
from web_app.resources import ReportResource, AdminResource, MediaResource, CommentResource, UpVoteResource
from web_app.models import Admin, Report, Media, UpVote, Comment
from base_map.models import BaseSite, Shape, Point, Polygon, MultiPolygon, Line, MultiLine, AdministrativeUnit, AdministrativeGroup
from tastypie.authentication import SessionAuthentication


class BaseSiteResource(ModelResource):
	my_map = fields.ForeignKey('api.resources.MapResource', 'my_map', null=False, blank=False, full=False)
	shapes = fields.ToManyField('api.resources.ShapeResource', '_shape', null=True, blank=True, full_detail=True, full=True)
	
	def renderList(self, options={}):
		request = HttpRequest()
		request.GET = {'format': 'json'}
		if len(options) > 0:
			request.GET.update(options)

		resp = self.get_list(request)
		return resp.content

	class Meta:
		queryset = BaseSite.subclass_manager.all()
		serializer = GeoJsonSerializer()
		filtering = {
			'my_map': ALL
		}
		#authentication = SessionAuthentication()

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		excludes = ['password', 'is_superuser']
		authentication = SessionAuthentication()

class AdministrativeUnitResource(ModelResource):
	report_set = fields.ToManyField('mtaasafi.resources.ReportResource', 'report_set', null=True, blank=True, full=False)

	class Meta:
		queryset = AdministrativeUnit.objects.all()

class AdministrativeUnitDetailResource(ModelResource):
	report_set = fields.ToManyField('mtaasafi.resources.ReportResource', 'report_set', null=True, blank=True, full=True)
	shapes = fields.ToManyField('api.resources.ShapeResource', '_shape', null=True, blank=True, full_detail=True, full=True)
	class Meta:
		resource_name = 'administrativeunitdetail'
		queryset = AdministrativeUnit.objects.all()

class AdministrativeGroupResource(ModelResource):
	admin_units = fields.ToManyField('administration.resources.AdministrativeUnitResource', 'administrativeUnits', null=True, blank=True, full=True)
	class Meta:
		queryset = AdministrativeGroup.objects.all()

	def dehydrate(self, bundle):
		me = AdministrativeGroup.objects.get(pk=bundle.data["id"])
		bundle.data["topojson"] = json.dumps(me.topojson)
		return bundle

class ShapeResource(ModelResource):
	content_object = GenericForeignKeyField({
		BaseSite: BaseSiteResource,
		AdministrativeUnit: AdministrativeUnitDetailResource,
		Report: ReportResource
	}, 'content_object', null=True, blank=True)

	class Meta:
		queryset = Shape.objects.all()
		serializer = GeoJsonSerializer()
		authentication = SessionAuthentication()

	def dehydrate(self, bundle):
		obj = Shape.objects.filter(pk=bundle.data["id"]).select_subclasses()[0]
		if not obj:
			obj = bundle.obj
		if obj:
			geom_resource = self.chooseResource(obj)
			new_bundle = geom_resource.build_bundle(obj=obj)
			bundle = geom_resource.full_dehydrate(new_bundle)
		return bundle

	def chooseResource(self, GeomModel):
		if GeomModel.__class__.__name__ == "Point":
			return PointResource()
		elif GeomModel.__class__.__name__ == "Polygon":
			return PolygonResource()
		elif GeomModel.__class__.__name__ == "MultiPolygon":
			return MultiPolygonResource()
		elif GeomModel.__class__.__name__ == "MultiLine":
			return MultiLineResource()
		elif GeomModel.__class__.__name__ == "Line":
			return LineResource()

class PointResource(ShapeResource):
	class Meta:
		# queryset = Point.geo_objects.all()
		serializer = GeoJsonSerializer() # From polyUpdate branch
		queryset = Point.objects.all()
	def dehydrate(self, bundle):
		return bundle

class PolygonResource(ShapeResource):
	class Meta:
		queryset = Polygon.objects.all()
		serializer = GeoJsonSerializer()
	def dehydrate(self, bundle):
		return bundle

class MultiPolygonResource(ShapeResource):
	class Meta:
		queryset = MultiPolygon.objects.all()
		serializer = GeoJsonSerializer()
	def dehydrate(self, bundle):
		return bundle

class MultiLineResource(ShapeResource):
	class Meta:
		queryset = MultiLine.objects.all()
		serializer = GeoJsonSerializer()
	def dehydrate(self, bundle):
		return bundle

class LineResource(ShapeResource):
	class Meta:
		queryset = Line.objects.all()
		serializer = GeoJsonSerializer()
	def dehydrate(self, bundle):
		return bundle

