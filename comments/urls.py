from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^page/(?P<page_pk>\d+)/comment/$', views.comment_page, name='comment_page'),
    url(r'^(?P<comment_pk>\d+)/reply/$', views.reply, name='reply'),
    url(r'^delete/(?P<model>[\w-]+)/(?P<pk>\d+)/$', views.delete, name='delete'),
    url(r'^(?P<model>[\w-]+)/(?P<pk>\d+)/comment/$', views.comment, name='comment'),
#    url(r'^campaign/(?P<campaign_pk>\d+)/comment/$', views.comment_campaign, name='comment_campaign'),
]
