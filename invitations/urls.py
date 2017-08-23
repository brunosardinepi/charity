from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^pending/$', views.pending_invitations, name='pending_invitations'),
]
