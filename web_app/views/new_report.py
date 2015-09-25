import json, hashlib, time, datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.contrib.gis.geos import *
from django.contrib.auth.models import User
import base_map
from web_app.signals import post_created

from base_map.models import AdministrativeGroup, AdministrativeUnit
from web_app.models import *
from web_app.decorators import request_resolver
from upvotes import upvote_helper

@csrf_exempt
@request_resolver
def add_post(request, report_type):
	if request.method == 'POST':
		report = None
		try:
			if request.body:
				report_json = json.loads(request.body)
				report, created = Report.objects.get_or_create(description=report_json['description'], status=report_json['status'], timestamp=timestamp_to_datetime(report_json['timestamp']), owner=User.objects.get(pk=report_json['userId']))
				point = addGPSData(report, report_json)

				getGeoAdmin(report, point)
				addMedia(report, report_json)
				addParent(report, report_json)
				addUpvotes(report, report_json)
				addTags(report, report_json)

				report.save()
				
				return HttpResponse(json.dumps({'id': report.pk, 'nextfield': 1, 'output': report.name }), status=201, content_type='application/json')
			else:
				return HttpResponseBadRequest()
		except Exception as e:
			if report: report.corrupt_flag = True
			return HttpResponseServerError(e)
	else:
		return HttpResponseBadRequest()

def addGPSData(report, report_json):
	# {"location": {"latitude": -1.244, "longitude": 36.3243, "timestamp": 241124321431, "accuracy": 23.123} }
	if report_json.has_key('location'):
		point = base_map.models.Point(shape='POINT( ' + str(report_json['location']['longitude']) + ' ' + str(report_json['location']['latitude']) + ')')
		report.location_accuracy = report_json['location']['accuracy']
		report.location_provider = report_json['location']['provider']
		report.location_timestamp = timestamp_to_datetime(report_json['location']['timestamp'])
	else:
		point = base_map.models.Point(shape='POINT( ' + str(report_json['longitude']) + ' ' + str(report_json['latitude']) + ')')
	report._shape.add(point)
	
	return point

def getGeoAdmin(report, point):
	admin_ctype = ContentType.objects.get(app_label='administration', model='administrativeunit')
	polys = base_map.models.Polygon.geo_objects.filter(content_type=admin_ctype)
	multipolys = base_map.models.MultiPolygon.geo_objects.filter(content_type=admin_ctype)
	if polys.filter(shape__contains=point.shape).exists():
		report.geo_admin = AdministrativeUnit.objects.get(_shape=polys.filter(shape__contains=point.shape)[0])
	elif multipolys.filter(shape__contains=point.shape).exists():
		report.geo_admin = AdministrativeUnit.objects.get(_shape=multipolys.filter(shape__contains=point.shape)[0])

	if report.geo_admin and not report.geo_admin.report_set.all().count() > 1:
			AdministrativeGroup.objects.get(name="MtaaSafi Kenya").administrativeUnits.add(report.geo_admin)
	

def addMedia(report, report_json):
	if report_json.has_key('picHashes'):
		for picHash in report_json['picHashes']:
			Media.objects.create(report=report, timestamp=report.timestamp, sha1_hash=picHash)

def addUpvotes(report, report_json):
	if report_json.has_key('upvote_data'):
		upvote_data = upvote_helper(report_json['upvote_data'])
		return HttpResponse(json.dumps({'id': report.pk, 'nextfield': 1, 'output': report.name, 'upvote_data': upvote_data }), status=201, content_type="application/json")

def addParent(report, report_json):
	if report_json.has_key("parent_id"):
		report.parent = Report.objects.get(pk=report_json["parent_id"])

def addTags(report, report_json):
	if report_json.has_key("tags"):
		for t in report_json["tags"]:
			tag, created = Tag.objects.get_or_create(name=t)
			report.tags.add(tag)

@csrf_exempt
def add_post_media_from_stream(request, reportID, screenW=400):
	if request.method == 'POST':
		report = get_object_or_404(Report, pk=reportID)
		picHash = hashlib.sha1(str(request.body)).hexdigest()
		try:
			m = Media.objects.get(report=report, sha1_hash=picHash)
			m.image = ContentFile(request.body, 'image_'+str(report.pk)+'.jpg')
			m.save()
			nextfield = Media.objects.filter(report=report).exclude(image='').count()+1

			for media in report.media_set.all():
				if not media.image:
					break
				report.incomplete_flag = False
				report.save()
				post_created.send(sender=Report, instance=report)
				
			return HttpResponse(json.dumps({ 'id':reportID, 'nextfield':nextfield, 'output': m.pk }), content_type="application/json")
		except Exception as e:
			return HttpResponseBadRequest(e)
	else:
		report = get_object_or_404(Report, pk=reportID)
		media = Media.objects.filter(report=report)
		count = 0
		mediaHashes = []
		nextfield = lambda x: x+1
		if media.exists:
			count = media.count()
			for m in media:
				mediaHashes.append(m.sha1_hash)
		return HttpResponse(json.dumps({"id": report.id, "description": report.description, "user": report.owner.username, "pic_count":count, "pic_hashes":mediaHashes, "nextfield":nextfield(count) }), content_type='application/json')
		
def timestamp_to_datetime(ts):
	return datetime.datetime.utcfromtimestamp(ts/1e3)
