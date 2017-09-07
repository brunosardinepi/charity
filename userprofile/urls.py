from django.conf.urls import url

from . import views


app_name = 'userprofile'
urlpatterns = [
    url(r'^$', views.userprofile, name='userprofile'),
]
