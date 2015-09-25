from django.contrib.gis.db import models
from django.contrib.auth.models import User
from users import MtaaSafiUserMeta
from reports import Report

class Group(models.Model):
	name = models.CharField(max_length=55)
	description = models.CharField(max_length=255)
	members = models.ManyToManyField(User, related_name="members")
	admins = models.ManyToManyField(User, related_name="admins")
	reports = models.ManyToManyField(Report, related_name="reports")

	class Meta:
		app_label = "web_app"

	def __unicode__(self):
		return self.name
