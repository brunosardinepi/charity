from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^accept/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', views.accept_invitation, name='accept_invitation'),
    url(r'^decline/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', views.decline_invitation, name='decline_invitation'),
    url(r'^pending/$', views.pending_invitations, name='pending_invitations'),
]
