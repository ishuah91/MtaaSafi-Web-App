from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from web_app.models.users import MtaaSafiUserMeta
import json

@csrf_exempt
def sign_in_user(request):
	if request.method == 'POST' and request.body:
		user_json = json.loads(request.body)
		if user_json.has_key("social_id") and user_json.has_key("name") and user_json.has_key("network"):
			
			if user_json.has_key("email"):
				user = _update_user_data(user_json)
			else:
				user, user_created = User.objects.get_or_create(username=user_json["name"])
				if user_created:
					user.set_password(User.objects.make_random_password())

			usermeta, created = MtaaSafiUserMeta.objects.get_or_create(user=user)
			if user_json["network"] == "google":
				usermeta.google_user_id = user_json["social_id"]
			elif user_json["network"] == "facebook":
				usermeta.facebook_user_id = user_json["social_id"]
			usermeta.save()

			return HttpResponse(json.dumps({ 'userId': user.pk }), status=201, content_type="application/json")
		return HttpResponseBadRequest("Missing key/value pair")
	return HttpResponseBadRequest()

def _update_user_data(user_json):
	try:
		user = User.objects.get(username=user_json["email"], email=user_json["email"])
		user.username = user_json["name"]
		user.save()
	except IntegrityError as e:
		user = User.objects.get(username=user_json["email"], email=user_json["email"])
		user.username = user_json["name"]+" ["+user_json["network"]+"]"
		user.save()
	except User.DoesNotExist as e:
		user, created = User.objects.get_or_create(username=user_json["name"], email=user_json["email"] )
		if created:
			user.set_password(User.objects.make_random_password())

	return user
