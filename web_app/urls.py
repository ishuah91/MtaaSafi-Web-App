from django.conf.urls import *
from django.contrib import admin, admindocs
from tastypie.api import Api

from web_app.resources import ReportResource, MtaaSafiUserMetaResource, AdminResource, AdminAreaResource, MediaResource, CommentResource, UpVoteResource, TagResource, GroupResource
admin.autodiscover()
v1_api = Api(api_name='v1')
v1_api.register(ReportResource())
v1_api.register(MtaaSafiUserMetaResource())
v1_api.register(AdminResource())
v1_api.register(AdminAreaResource())
v1_api.register(CommentResource())
v1_api.register(MediaResource())
v1_api.register(UpVoteResource())
v1_api.register(TagResource())
v1_api.register(GroupResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
    url(r'^$', 'web_app.views.view_all', name='mtaasafi'),
    url(r'^community/(?P<communityId>\d+)/$', 'web_app.views.view_community'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'web_app/login.html'},  name='mtaasafi_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/all'}, name='mtaasafi_login_logout' ),
    
    url(r'^fetch_reports/(?P<userId>\d+)/(?P<longitude>[-\d.]{0,180})/(?P<latitude>[-\d.]{0,90})/$', 'web_app.views.get_geolocated_report_ids'),
    url(r'^fetch_reports/(?P<userId>\d+)/(?P<adminId>\d+)/$', 'web_app.views.get_admin_report_ids'),
    url(r'^fetch_report_details/(?P<screenW>\d+)/$', 'web_app.views.get_reports'),
    url(r'^add_post/$', "web_app.views.add_post"),
    url(r'^add_post_from_stream/(?P<reportID>\d+)/$', 'web_app.views.add_post_media_from_stream'),
    url(r'^add_post_from_stream/(?P<reportID>\d+)/(?P<screenW>\d+)/$', 'web_app.views.add_post_media_from_stream'),
    url(r'^post_comments/$', 'web_app.views.post_comment'),
    url(r'^post_upvotes/$', 'web_app.views.upvote'),
    url(r'^get_comments/(?P<reportID>\d+)/$', 'web_app.views.get_comments'),
    url(r'^get_comments/(?P<reportID>\d+)/(?P<timestamp>\d+)/$', 'web_app.views.get_comments'),
    url(r'^get_report_history/(?P<reportID>\d+)/$', 'web_app.views.get_report_history'),
    url(r'^upvote/$', 'web_app.views.upvote'),
    url(r'^get_location_data/$', 'web_app.views.get_location_data'),
    #url(r'^', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls',  namespace='rest_framework')),

    url(r'^get_thumbnail/(?P<imageId>[\d]{0,50})/(?P<dimensions>[\w\s\d]{0,500})/$', 'web_app.views.get_thumbnail'),
    url(r'^sign_in_user/$', 'web_app.views.sign_in_user'),
)
