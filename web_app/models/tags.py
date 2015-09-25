from django.db import models

class Tag(models.Model):
	name = models.CharField(max_length=255, unique=True)
	
	class Meta:
		app_label = "web_app"

	def __unicode__(self):
		return self.name

