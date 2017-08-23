from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.pending_invitations, name='pending_invitations'),
]
