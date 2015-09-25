from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import *
from django.http import HttpResponse, HttpResponseBadRequest
from base_map.models import BaseSite, Point, AdministrativeUnit, AdministrativeGroup
from web_app.models import *

def view_all(request):
	return render(request, 'web_app/main.html', { 'adminGroupId': 1 })

def view_community(request, communityId=None):
    community = get_object_or_404(AdministrativeUnit, pk=communityId)
    return render(request, 'web_app/community.html', { 'community': community })