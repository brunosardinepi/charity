from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^page/(?P<page_pk>\d+)/comment/$', views.comment_page, name='comment_page'),
    url(r'^campaign/(?P<campaign_pk>\d+)/comment/$', views.comment_campaign, name='comment_campaign'),
]
