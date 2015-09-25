from django.contrib.gis.db import models
from base_map.models.shapes import *
from django.contrib.gis.geos import *
from jsonfield import JSONField


class AdministrativeUnit(ShapeMixin, models.Model):
	name = models.CharField(max_length=255)
	divisionType = models.CharField(max_length=255)
	_shape = generic.GenericRelation(Shape,content_type_field='content_type',object_id_field='object_id')
	objects = GeoInheritanceManager()

	neighbors = models.ManyToManyField('self', symmetrical=True, related_name='neighboring+')
	
	class Meta:
		app_label= "base_map"
	def __unicode__(self):
		return self.name

class AdministrativeGroup(models.Model):
	name = models.CharField(max_length=255)
	adminType = models.CharField(max_length=255)
	topojson = JSONField(null=True, blank=True)
	administrativeUnits = models.ManyToManyField(AdministrativeUnit, blank=True)
	objects = GeoInheritanceManager()

	class Meta:
		app_label = "base_map"

	def __unicode__(self):
		return self.name