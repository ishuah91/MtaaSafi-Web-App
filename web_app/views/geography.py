from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.http import HttpResponse, HttpResponseNotFound
from django.core import serializers
from base_map.models import AdministrativeGroup
import json
import base_map

#need to nest landmarks and admin areas together
def get_location_data(request):
	response_json = {"admins": []}
	admins = AdministrativeGroup.objects.get(name="MtaaSafi Kenya").administrativeUnits.all()
	if admins:
		for admin in admins:
			admin_json = { "admin": admin.name, "adminId":admin.pk }
			response_json["admins"].append(admin_json)

	if response_json:
		return HttpResponse(json.dumps(response_json), content_type='application/json')
	return HttpResponseNotFound()