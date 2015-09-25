from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from base_map.models.inheritance_managers import *

class ShapeMixin(object):
    @property
    def shape(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            shape_model = Shape.objects.all().select_subclasses().get(content_type=ctype, object_id=self.id)
            return shape_model.shape
        except:
            return None

class Shape(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()

    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_shape'
        unique_together = ('content_type', 'object_id')
        
class Point(Shape):
    shape = models.PointField()
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()

    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_point'

class Polygon(Shape):
    shape = models.PolygonField()
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()

    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_polygon'

class MultiPolygon(Shape):
    shape = models.MultiPolygonField()
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()

    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_multipolygon'

class Polygon3D(Shape):
    shape = models.PolygonField(dim=3)
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()

    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_polygon3d'

class MultiPolygon3D(Shape):
    shape = models.MultiPolygonField(dim=3)
    objects = GeoInheritanceManager()

    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_multipolygon3d'
        
class Line(Shape):
    shape = models.LineStringField()
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()
    class Meta:
        app_label = 'base_map'
        db_table = 'base_map_line'

class MultiLine(Shape):
    shape = models.MultiLineStringField()
    objects = GeoInheritanceManager()
    geo_objects = models.GeoManager()
    
    class Meta:
        app_label ='base_map'
        db_table = 'base_map_multiline'

