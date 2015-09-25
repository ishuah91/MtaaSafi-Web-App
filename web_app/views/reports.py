import json, hashlib, time, datetime, calendar
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from sorl import thumbnail

import base_map
from web_app.models import *
from base_map.models import AdministrativeUnit
from upvotes import upvote_helper

@csrf_exempt
def get_geolocated_report_ids(request, userId, longitude="36.8223", latitude="-1.295"):
	distance = 10
	point = Point(float(longitude), float(latitude))
	points_qs = base_map.models.Point.geo_objects.filter(content_type=ContentType.objects.get(app_label='web_app', model='report'), shape__distance_lte=(point, D(km=distance))).distance(point).order_by('distance')

	reports_qs = getReportsFromQS(points_qs)
	reports_qs = getUserReports(userId, reports_qs);
	reports_qs = filterUpdatedReports(reports_qs)
	reports_qs = reports_qs.order_by("-timestamp")

	report_ids = [ report['id'] for report in reports_qs.values('id')[0:101]]

	logUserLocation(userId, point)

	return HttpResponse(json.dumps({ "ids": report_ids }), content_type='application/json')

@csrf_exempt
def get_admin_report_ids(request, userId, adminId):
	admin = AdministrativeUnit.objects.get(pk=adminId)
	points_qs = base_map.models.Point.geo_objects.filter(content_type=ContentType.objects.get(app_label='web_app', model='report'), shape__within=admin.shape)[0:101]

	reports_qs = getReportsFromQS(points_qs)
	reports_qs = getUserReports(userId, reports_qs);
	return HttpResponse(json.dumps({ "ids": reports_qs }), content_type='application/json')

def getReportsFromQS(querySet):
	reports_qs = Report.objects.filter(_shape__in=querySet).exclude(corrupt_flag=True)
	return reports_qs

def getUserReports(userId, reports_qs):
	user_reports = Report.objects.filter(owner=User.objects.get(pk=userId)).exclude(corrupt_flag=True)
	reports_qs = user_reports | reports_qs
	return reports_qs

def filterUpdatedReports(reports_qs):
	for report in reports_qs:
		if Report.objects.filter(parent=report).exists():
			reports_qs = reports_qs.exclude(pk=report.pk)
	return reports_qs

@csrf_exempt
def get_reports(request, screenW=240):
	if request.method == 'POST':
		request_json = json.loads(request.body)
		response_json = {}
		response_json['reports'] = []
		if request_json.has_key('upvote_data'):
			response_json['upvote_data'] = upvote_helper(request_json['upvote_data'])

		for pk in request_json['ids']:
			report = Report.objects.get(pk=pk)
			report_json = createJson(report, request_json['userId'])
			if report_json:
				response_json['reports'].append(report_json)

		return HttpResponse(json.dumps(response_json), content_type="application/json")
	else:
		return HttpResponseBadRequest()

def createJson(report, userId):
	if report.geo_admin:
		geo_admin_id = report.geo_admin.pk
	else:
		geo_admin_id = -1

	if report.parent:
		parent = report.parent.pk
	else:
		parent = 0

	media = Media.objects.filter(report=report).exclude(image='')
	mediaIds = []
	for m in media:
		mediaIds.append(m.pk)

	commentIds = []
	for comment in Comment.objects.filter(report=report):
		commentIds.append(comment.pk)
	try:
		return { "unique_id": report.pk, 
			"place":report.name, 
			"description": report.description,
			"status": report.status,
			"user_id":report.owner.pk,
			"username":report.owner.username,
			"admin_id": geo_admin_id,
			"media": mediaIds,
			"timestamp": datetime_to_timestamp(report.timestamp),
			"type":report.report_type,
			"latitude":report.shape.y,
			"longitude":report.shape.x,
			"parent":parent,
			'upvote_count': UpVote.objects.filter(report=report).count(),
			'upvoted': UpVote.objects.filter(owner=User.objects.get(pk=userId), report=report).exists(),
			'commentIds': commentIds }
	except Exception as e:
		return None


def datetime_to_timestamp(dt):
	return int(calendar.timegm(dt.timetuple())*1e3 + (dt.microsecond/1e3))

def get_thumbnail(request, imageId=None, dimensions=None):
    return HttpResponse(thumbnail.get_thumbnail(Media.objects.get(pk=imageId).image.url, dimensions, crop='center').read(), content_type="image/jpeg")

def get_report_history(request, reportID):
	root_report = Report.objects.get(pk=reportID)
	reports = fetchParentReports(root_report, Report.objects.none())
	reports = reports.order_by("-timestamp")
	status  = root_report.status
	response_json = {"reports": []}
	for report in reports:
		if report.parent == None:
			response_json["reports"].append({ "event": "Report created", "timestamp":datetime_to_timestamp(report.timestamp), "status":report.status })
			status = report.status
		else:
			if report.status != status:
				response_json["reports"].append({ "event": "Status changed", "timestamp":datetime_to_timestamp(report.timestamp), "status":report.status })
				status = report.status

	if root_report.status != status:
		response_json["reports"].insert(0, { "event": "Status changed", "timestamp":datetime_to_timestamp(root_report.timestamp), "status":root_report.status })

	return HttpResponse(json.dumps(response_json), content_type="application/json")

def fetchParentReports(report, reports):
	if not report.parent:
		return reports
	else:
		reports = fetchParentReports(report.parent, reports | Report.objects.filter(pk=report.parent.pk))
		return reports

def logUserLocation(userId, point):
	usermeta = MtaaSafiUserMeta.objects.get(user=User.objects.get(pk=userId))
	usermeta.whereabouts = point
	usermeta.save()
