from django.contrib.gis.db import models
from django.contrib.auth.models import User
from gcm.models import Device
from datetime import datetime

class MtaaSafiUserMeta(models.Model):
	user = models.OneToOneField(User)
	google_user_id = models.CharField(max_length=255, blank=True, null=True)
	facebook_user_id = models.CharField(max_length=255, blank=True, null=True)
	device = models.ForeignKey(Device, blank=True, null=True)
	whereabouts = models.PointField(null=True, blank=True)
	objects = models.GeoManager()

	last_update_timestamp = models.DateTimeField(default=datetime(2010, 1, 1))

	class Meta:
		app_label = "web_app"

	def __unicode__(self):
		return self.user.username