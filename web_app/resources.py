import time
from datetime import datetime
from tastypie import fields
from tastypie.contrib.gis.resources import ModelResource
from tastypie.bundle import Bundle
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.authorization import Authorization
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.contrib.gis import geos
from django.http import HttpRequest
from django.contrib.gis.measure import D
from tastypie.contrib.gis.resources import ModelResource
from django.contrib.auth.models import User
from base_map.models import Shape, Point, Polygon, MultiPolygon
from web_app.models import Report, Media, UpVote, Comment, MtaaSafiUserMeta, Tag, Group
from base_map.models.administrativeUnits import *

class ReportResource(ModelResource):
	shapes = fields.ToManyField('api.resources.ShapeResource', '_shape', null=True, blank=True, full_detail=True, full=True)
	owner = fields.ToOneField('api.resources.UserResource', 'owner', null=True, blank=True, full=True)
	parent = fields.ToOneField('api.resources.ReportResource', 'parent', null=True, blank=True)
	geo_admin = fields.ToOneField('api.resources.AdminResource', 'geo_admin', null=True, blank=True, full=True)

	tags = fields.ToManyField('web_app.resources.TagResource', 'tags', null=True, blank=True, full=True)
	upvote_set = fields.ToManyField('web_app.resources.UpVoteResource', 'upvote_set', null=True, blank=True, full=True)
	media_set = fields.ToManyField('web_app.resources.MediaResource', 'media_set', null=True, blank=True, full=True)
	comment_set = fields.ToManyField('web_app.resources.CommentResource', 'comment_set', null=True, blank=True, full=True)

	def __init__(self, api_name=None):
		self.Error_Message = ""
		self.Actual_Total = 0
		self.User_Report_Count = 0
		self.Nearby_Admins = []
		self.User_Upvotes = []
		super(ReportResource, self).__init__(api_name)

	def renderList(self, options={}):
		request = HttpRequest()
		request.GET = {'format': 'json'}
		if len(options) > 0:
			request.GET.update(options)

		resp = self.get_list(request)
		return resp.content

	def apply_filters(self, request, applicable_filters):
		self.Error_Message = ""
		self.Actual_Total = 0
		self.User_Report_Count = 0
		self.Nearby_Admins = []
		self.User_Upvotes = []
		report_list = super(ReportResource, self).apply_filters(request, applicable_filters)

		lat = request.GET.get('lat', None)
		lng = request.GET.get('lng', None)
		point = None
		adminId = request.GET.get('adminId', None)
		userId = request.GET.get('userId', None)

		if lat and lng:
			point = geos.Point(float(lng), float(lat))
			report_list = self.getReportsNear(point, request.GET.get('dist', 100), report_list)
			if not report_list.exists():
				self.Error_Message = "nothing_nearby"
		elif adminId and AdministrativeUnit.objects.filter(pk=adminId).exists():
			report_list = report_list.filter(geo_admin=AdministrativeUnit.objects.get(pk=adminId))
			if not report_list.exists():
				self.Error_Message = "nothing_in_admin"
		self.Actual_Total = report_list.count()

		if userId and User.objects.filter(pk=userId).exists():
			user = User.objects.get(pk=userId)
			self.User_Upvotes = UpVote.objects.filter(owner=user).values_list("report", flat=True)
			self.User_Report_Count = Report.objects.filter(corrupt_flag=False, incomplete_flag=False, owner=user).count()
			if request.GET.get('userOnly', False) == 'true':
				report_list = Report.objects.filter(corrupt_flag=False, incomplete_flag=False, owner=user)
			elif request.GET.get('all', 'false') == 'false' and MtaaSafiUserMeta.objects.filter(user=user).exists():
				prev_update_timestamp = self.updateUserMetaData(user, point)
				report_list = report_list.filter(last_update_timestamp__gte=prev_update_timestamp)

		return report_list

	def alter_list_data_to_serialize(self, request, data):
		if self.Error_Message: data['meta']['error'] = self.Error_Message
		if self.Nearby_Admins: data['meta']['nearby_admins'] = self.Nearby_Admins
		if self.User_Report_Count: data['meta']['user_report_count'] = self.User_Report_Count
		if self.User_Upvotes: data['meta']['user_upvotes'] = self.User_Upvotes
		if self.Actual_Total: data['meta']['actual_total'] = self.Actual_Total
		return data

	def dehydrate(self, bundle):
		dt = bundle.data['timestamp']
		timestamp = int(time.mktime(dt.timetuple())*1e3 + (dt.microsecond/1e3))
		bundle.data['timestamp'] = timestamp
		return RemoveNullValues(self, bundle)

	class Meta:
		queryset = Report.objects.exclude(corrupt_flag=True).exclude(incomplete_flag=True).order_by("timestamp")
		authorization = Authorization()
		filtering = { 'id': ALL }

	def getReportsNear(self, point, dist, report_list):
		shape = None
		ct = ContentType.objects.get(app_label='administration', model='administrativeunit')
		polys = Polygon.geo_objects.filter(content_type=ct).filter(shape__contains=point)
		if polys.exists():
			shape = polys[0]
		else:
			mpolys = MultiPolygon.geo_objects.filter(content_type=ct).filter(shape__contains=point)
			if mpolys.exists():
				shape = mpolys[0]
		if shape:
			admins = AdministrativeUnit.objects.filter(_shape=shape) | AdministrativeUnit.objects.get(_shape=shape).neighbors.all()
			self.Nearby_Admins = admins.values_list('pk', flat=True)
			return report_list.filter(geo_admin__in=admins)
		return Report.objects.none()

	def updateUserMetaData(self, user, point):
		usermeta = MtaaSafiUserMeta.objects.get(user=user)
		prev_update_timestamp = usermeta.last_update_timestamp
		usermeta.last_update_timestamp = datetime.now()
		if point:
			usermeta.whereabouts = point
		usermeta.save()
		return prev_update_timestamp

class MtaaSafiUserMetaResource(ModelResource):
	user = fields.ToOneField('api.resources.UserResource', 'user', null=True, blank=True, full=True)

	def dehydrate(self, bundle):
		return RemoveNullValues(self, bundle)

	class Meta:
		queryset = MtaaSafiUserMeta.objects.all()

class AdminResource(ModelResource):
	report_set = fields.ToManyField('web_app.resources.ReportResource', 'report_set', null=True, blank=True, full=False)
	class Meta:
		queryset = AdministrativeUnit.objects.all() #AdministrativeUnit.objects.annotate(num_reports=Count('report')).filter(num_reports__gt=0)

class AdminAreaResource(ModelResource):
	shapes = fields.ToManyField('api.resources.ShapeResource', '_shape', null=True, blank=True, full_detail=True, full=True)
	report_set = fields.ToManyField('web_app.resources.ReportResource', 'report_set', null=True, blank=True, full=True)

	class Meta:
		resource_name = 'adminarea'
		queryset = AdministrativeUnit.objects.all() #AdministrativeUnit.objects.annotate(num_reports=Count('report')).filter(num_reports__gt=0)

class MediaResource(ModelResource):
	class Meta:
		queryset = Media.objects.all()

class CommentResource(ModelResource):
	owner = fields.ToOneField('api.resources.UserResource', 'owner', null=True, blank=True, full=True)
	class Meta:
		queryset = Comment.objects.all()
		filtering = { 'id': ALL }

	def renderList(self, options={}):
		request = HttpRequest()
		request.GET = {'format': 'json'}
		if len(options) > 0:
			request.GET.update(options)

		resp = self.get_list(request)
		return resp.content
		
	def dehydrate(self, bundle):
		dt = bundle.data['timestamp']
		timestamp = int(time.mktime(dt.timetuple())*1e3 + (dt.microsecond/1e3))
		bundle.data['timestamp'] = timestamp
		return bundle

class UpVoteResource(ModelResource):
	# owner = fields.ToOneField('api.resources.UserResource', 'owner', null=True, blank=True, full=True)
	class Meta:
		queryset = UpVote.objects.all()

class TagResource(ModelResource):
	class Meta:
		queryset = Tag.objects.all()

class GroupResource(ModelResource):
	members = fields.ToManyField('api.resources.UserResource', 'members', null=True, blank=True, full_detail=True, full=True)
	admins = fields.ToManyField('api.resources.UserResource', 'admins', null=True, blank=True, full_detail=True, full=True)
	reports = fields.ToManyField('web_app.resources.ReportResource', 'reports', null=True, blank=True, full_detail=False, full=False)
	class Meta:
		queryset = Group.objects.all()
		filtering = {   'members': ALL_WITH_RELATIONS,
						'admins': ALL_WITH_RELATIONS }
		authorization = Authorization()

def RemoveNullValues(self, bundle):
	# Fix for removing fields with null values since blank=True doesn't seem to do shit (and android can't handle null)
	for field_name, field_obj in self.fields.items():
		if field_obj.blank and bundle.data.has_key(field_name) and bundle.data[field_name] == None:
			bundle.data.pop(field_name, None)
		elif not field_obj.blank and not bundle.data.has_key(field_name):
			raise ApiFieldError("The '%s' field has no data and doesn't allow a default or null value." % field_name)
	return bundle
