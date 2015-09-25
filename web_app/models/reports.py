from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.gis.geos import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.measure import D
from django.contrib.auth.models import User
from tags import Tag
import base_map
from base_map.models.shapes import *
from base_map.models.sites import *
from geography import Admin, Landmark
from base_map.models import AdministrativeUnit

class Report(BaseSite):
	BROKEN = 0
	IN_PROGRESS = 1
	FIXED = 2
	STATUS_CHOICES = (
		(BROKEN, 'Broken'),
		(IN_PROGRESS, 'In Progress'),
		(FIXED, 'Fixed'),
	)

	description = models.TextField()
	status = models.SmallIntegerField(choices=STATUS_CHOICES, default=BROKEN)

	corrupt_flag = models.BooleanField(default=False, blank=False, null=False)
	incomplete_flag = models.BooleanField(default=True, blank=False, null=False)
	
	last_update_timestamp = models.DateTimeField(blank=True, null=True)

	location_accuracy = models.FloatField(blank=True, null=True)
	location_timestamp = models.DateTimeField(blank=True, null=True)
	location_provider = models.CharField(blank=True, null=True, max_length=20)
	
	owner = models.ForeignKey(User)
	geo_admin = models.ForeignKey(AdministrativeUnit, blank=True, null=True, on_delete=models.SET_NULL)
	user_admin = models.ForeignKey(Admin, blank=True, null=True, on_delete=models.SET_NULL, related_name="user_report_set")
	landmark = models.ForeignKey(Landmark, blank=True, null=True, on_delete=models.SET_NULL)
	parent = models.ForeignKey("Report", blank=True, null=True)
	
	tags = models.ManyToManyField(Tag)
	
	class Meta:
		app_label = "web_app"

	def __unicode__(self):
		return self.description + " by " + self.owner.username

	def save(self, *args, **kwargs):
		self.last_update_timestamp = datetime.now()
		if self.shape != None and self.name == 'temp':
			if self.geo_admin:
				self.name = self.geo_admin.name.replace('Ward', '')
			else:
				self.name = 'Unknown Location'
		super(Report, self).save(*args, **kwargs)

	def get_landmarks(self):
		radius = 100
		unit = 'm'
		point = GEOSGeometry(self.shape)
		
		landmark_ctype = ContentType.objects.get(app_label='web_app', model='landmark')
		points_qs = base_map.models.Point.geo_objects.filter(content_type=landmark_ctype, shape__distance_lte=(point, D(**{unit:radius}))).distance(point).order_by('distance')

		if len(points_qs) >= 2:
			return (Landmark.objects.get(_shape=points_qs[0]), Landmark.objects.get(_shape=points_qs[1]))
		elif len(points_qs) == 1:
			return Landmark.objects.get(_shape=points_qs[0])
		else:
			return False

	def get_media_ids(self):
		media = Media.objects.filter(report=self)
		media_ids = []
		for m in media:
			media_ids.append(m.pk)
		return media_ids

class Media(models.Model):
	report = models.ForeignKey(Report)
	image = models.ImageField(upload_to="mtaasafi", blank=True, null=False)
	timestamp = models.DateTimeField()
	sha1_hash = models.CharField(max_length=50)

	class Meta:
		app_label = 'web_app'

	def __unicode__(self):
		return "image for " + self.report.name

class UpVote(models.Model):
	owner = models.ForeignKey(User)
	report = models.ForeignKey(Report)

	class Meta:
		app_label = 'web_app'
		unique_together = ("owner", "report")

	def save(self, *args, **kwargs):
		self.report.last_update_timestamp = datetime.now()
		self.report.save()
		super(UpVote, self).save(*args, **kwargs)

class Comment(models.Model):
	owner = models.ForeignKey(User)
	report = models.ForeignKey(Report)
	comment = models.TextField()
	timestamp = models.DateTimeField()

	def save(self, *args, **kwargs):
		self.report.last_update_timestamp = datetime.now()
		self.report.save()
		super(Comment, self).save(*args, **kwargs)

	class Meta:
		app_label = 'web_app'

	def __unicode__(self):
		return self.comment
