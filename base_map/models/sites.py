from django.utils.datetime_safe import datetime
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from base_map.models.inheritance_managers import *
from base_map.models.shapes import *

class AbstractBaseSite(ShapeMixin, models.Model):
    name = models.CharField(max_length=100, blank=False, default="temp")
    timestamp = models.DateTimeField(blank=True, null=True)
    text = models.CharField(max_length=500, blank=True, null=True)

    picture = models.ImageField(upload_to="img", blank=True, null=False)

    _shape = generic.GenericRelation(Shape, content_type_field='content_type', object_id_field='object_id')
    
    objects = GeoInheritanceManager()
    subclass_manager = GeoSubclassManager()
    class Meta:
        abstract = True
        ordering = ['name']
        app_label = 'base_map'
        
    def __unicode__(self):
        return self.name

class BaseSite(AbstractBaseSite):
    @staticmethod
    def get_form_class():
        from base_map.models import BaseSiteForm
        return BaseSiteForm
    
    def get_fields(self):
        return self._meta.fields
    
    def get_field_details(self):
        return [(field.name, field.value_to_string(self)) for field in self._meta.fields]

    class Meta:
        verbose_name = 'site'
        app_label = 'base_map'
        db_table = 'base_map_basesite'