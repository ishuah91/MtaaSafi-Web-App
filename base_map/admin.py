from django.contrib import admin
from django.contrib.contenttypes import generic
from base_map.models import BaseSite, Shape, Point, Polygon, MultiPolygon, Line, MultiLine

class PointInline(generic.GenericTabularInline):
    max_num = 1
    model = Point
    
class PolygonInline(generic.GenericTabularInline):
    max_num = 1
    model = Polygon

class MultiPolygonInline(generic.GenericTabularInline):
    max_num = 1
    model = MultiPolygon
    
class LineInline(generic.GenericTabularInline):
    max_num = 1
    model = Line

class MultiLineInline(generic.GenericTabularInline):
    max_num = 1
    model = MultiLine

class BaseSiteAdmin(admin.ModelAdmin):
    inlines = [
        PointInline,
        PolygonInline,
        MultiPolygonInline,
        LineInline,
        MultiLineInline
    ]

admin.site.register(BaseSite, BaseSiteAdmin)
