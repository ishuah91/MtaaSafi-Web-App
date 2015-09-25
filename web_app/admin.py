from django.contrib import admin
from base_map.admin import BaseSiteAdmin
import models

class CommentInline(admin.TabularInline):
	model = models.Comment
class MediaInline(admin.TabularInline):
	model = models.Media
class UpVoteInline(admin.TabularInline):
	model = models.UpVote
class ReportAdmin(admin.ModelAdmin):
	inlines = [MediaInline, CommentInline, UpVoteInline]

admin.site.register(models.Report, ReportAdmin)
admin.site.register(models.Landmark, BaseSiteAdmin)
admin.site.register(models.Media)
admin.site.register(models.UpVote)
admin.site.register(models.Tag)
admin.site.register(models.Group)
admin.site.register(models.Admin, BaseSiteAdmin)
admin.site.register(models.MtaaSafiUserMeta)

