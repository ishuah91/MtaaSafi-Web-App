from gcm.signals import device_registered, device_unregistered
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.contrib.auth.models import User
from web_app.models.users import MtaaSafiUserMeta
from web_app.models.reports import Report, UpVote, Comment
from django.contrib.gis.measure import D
from django.contrib.gis.geos import *
from gcm.models import Device
from web_app.resources import ReportResource, CommentResource
import json

@receiver(device_registered)
def add_device_user(sender, **kwargs):
	request = kwargs.get('request')
	device = kwargs.get('device')
	user = User.objects.get(pk=json.loads(request.body)["userId"])
	usermeta, created = MtaaSafiUserMeta.objects.get_or_create(user=user)
	usermeta.device = device
	usermeta.save()

@receiver(post_save, sender=Comment)
@receiver(post_save, sender=UpVote)
def send_notification(sender, **kwargs):
	instance = kwargs.get('instance')
	if instance.report.owner != instance.owner:
		user = instance.report.owner
		usermeta = MtaaSafiUserMeta.objects.get(user=user)
		notification = { "reportId": instance.report.pk }
		if usermeta.device:
			if sender._meta.verbose_name == 'up vote':
				notification['type'] = "upvote"
				notification['title'] = instance.owner.username + " upvoted"
				notification['message'] = instance.report.description
			elif sender._meta.verbose_name == 'comment':
				notification['type'] = "comment"
				notification['title'] = instance.owner.username +  " commented"
				notification['message'] = instance.comment
				res = CommentResource()
				notification['data'] = json.loads(res.renderList({ 'id': instance.pk }))['objects'][0]
			print notification
			usermeta.device.send_message(json.dumps(notification))

post_created = Signal(providing_args=["instance"])
@receiver(post_created, sender=Report)
def send_new_report_notification(sender, **kwargs):
	instance = kwargs.get('instance')
	if instance.shape and not instance.incomplete_flag:
		radius = 5
		point = GEOSGeometry(instance.shape)
		usermeta = MtaaSafiUserMeta.objects.filter(whereabouts__distance_lte=(point, D(km=radius))).distance(point).order_by('distance').exclude(device__isnull=True).exclude(user=instance.owner)
		devices = Device.objects.filter(id__in=[um.device.pk for um in usermeta])
		res = ReportResource()

		report_json = json.loads(res.renderList({ 'id': instance.pk }))['objects'][0]
		notification = {"reportId": instance.id, "title": "New report near you", "message": instance.description, "type": "new", "data": report_json }
		devices.send_message(json.dumps(notification))

