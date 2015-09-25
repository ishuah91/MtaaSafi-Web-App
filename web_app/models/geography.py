from base_map.models.shapes import *
from base_map.models.sites import *
from django.contrib.gis.db import models
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D

class Admin(ShapeMixin, models.Model):
	name = models.CharField(max_length=100, default="")
	region_type = models.CharField(max_length=100, default="")
	region_parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
	_shape = generic.GenericRelation(Shape, content_type_field='content_type', object_id_field='object_id')
	objects = GeoInheritanceManager()

	class Meta:
		ordering = ['name']
		app_label = 'web_app'

	def __unicode__(self):
		return self.name

class Landmark(ShapeMixin, models.Model):
	PLACE_CHOICES = (
		('church', 'Church'),
		('mosque', 'Mosque'),
		('school', 'School'),
		('bar', 'Bar'),
		('shop', 'Shop'),
		('hospital', 'Hospital'),
		('hotel', 'Hotel'),
		('restaurant', 'Restaurant'),
		('other', 'Other'),
	)
	name = models.CharField(max_length=500)
	place_type = models.CharField(max_length=50)
	date_added = models.DateTimeField(auto_now_add=True)
	_shape = generic.GenericRelation(Shape, content_type_field='content_type', object_id_field='object_id')
	objects = GeoInheritanceManager()

	class Meta:
		ordering = ['name']
		app_label = 'web_app'

	def __unicode__(self):
		return self.name