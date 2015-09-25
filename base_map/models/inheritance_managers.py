from django.contrib.gis.db import models
from model_utils.managers import InheritanceQuerySet

class GeoInheritanceManager(models.GeoManager):
    def get_query_set(self):
        return InheritanceQuerySet(self.model)

class GeoSubclassManager(models.GeoManager):
    def get_query_set(self):
        return InheritanceQuerySet(self.model).select_subclasses()