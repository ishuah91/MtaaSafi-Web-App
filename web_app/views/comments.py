from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from web_app.models import Report, Comment
import json, time, datetime, calendar

@csrf_exempt
def post_comment(request):
	if request.method == 'POST':
		try:
			request_json = json.loads(request.body)
			response_json = {"comments": []}
			user = User.objects.get(pk=request_json['userId'])
			for comment in request_json["items"]:
				report = get_object_or_404(Report, pk=comment['reportId'])
				model = Comment(owner=user, timestamp=timestamp_to_datetime(comment['timestamp']), comment=comment['comment'], report=report)
				model.save()
				comment_json = {'id': model.pk ,'username': model.owner.username, 'timestamp': datetime_to_timestamp(model.timestamp), 'comment': model.comment, 'reportId':report.pk, 'clientId': comment["clientId"] }
				response_json["comments"].append(comment_json)
			
			return HttpResponse(json.dumps(response_json), content_type="application/json")
		except Exception as e:
			return HttpResponse(e)
	else:
		return HttpResponseBadRequest()

@csrf_exempt
def get_comments(request, reportID, timestamp = None):
	report = get_object_or_404(Report, pk=reportID)

	#report parents plus the original report, to make things easier
	reports = fetchParentReports(report, Report.objects.filter(pk=reportID))
	comments_json = []

	if timestamp:
		comments = Comment.objects.filter(report=reports, timestamp__gt=timestamp_to_datetime(float(timestamp)))
	else:
		comments = Comment.objects.filter(report=reports)

	for c in comments:
		comments_json.append({ 'commentId': c.pk, 'username': c.owner.username, 'timestamp': datetime_to_timestamp(c.timestamp), 'comment': c.comment, 'reportId':report.pk  })

	return HttpResponse(json.dumps({ 'comments':comments_json }), content_type="application/json")


def datetime_to_timestamp(dt):
	return int(calendar.timegm(dt.timetuple())*1e3 + (dt.microsecond/1e3))

def timestamp_to_datetime(ts):
	return datetime.datetime.utcfromtimestamp(ts/1e3)

def fetchParentReports(report, reports):
	if not report.parent:
		return reports
	else:
		reports = fetchParentReports(report.parent, reports | Report.objects.filter(pk=report.parent.pk))
		return reports