from django.conf.urls import url

from . import views


app_name = 'invitations'
urlpatterns = [
    url(r'^manager/accept/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', views.accept_invitation, name='accept_invitation'),
#    url(r'^accept/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', views.accept_general_invitation, name='accept_general_invitation'),
    url(r'^(?P<type>[\w-]+)/decline/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', views.decline_invitation, name='decline_invitation'),
]
