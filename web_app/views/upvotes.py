from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from web_app.models import Report, UpVote
import json

@csrf_exempt
def upvote(request):
	if request.method == 'POST':
		vote_json = json.loads(request.body)
		total_upvotes = {"reports": []}
		user = User.objects.get(pk=vote_json['userId'])
		for vId in vote_json["items"]:
			try:
				upvote = UpVote.objects.create(owner=user, report=Report.objects.get(pk=vId))
				total_upvotes["reports"].append({'id': vId, 'upvote_count': UpVote.objects.filter(report=Report.objects.get(pk=vId)).count()})
			except:
				return HttpResponseBadRequest()
		return HttpResponse(json.dumps(total_upvotes), status=201, content_type='application/json')
	else:
		return HttpResponseBadRequest()

def upvote_helper(upvotes_json):
	total_upvotes = []
	for upvote_json in upvotes_json['ids']:
		try:
			upvote = UpVote.objects.create(owner=User.objects.get(pk=upvotes_json['userId']), report=Report.objects.get(pk=upvote_json))
			total_upvotes.append({'id': upvote_json, 'upvote_count': UpVote.objects.filter(report=Report.objects.get(pk=upvote_json)).count()})
		except:
			pass
	return total_upvotes