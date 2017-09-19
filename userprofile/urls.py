from django.conf.urls import url

from . import views


app_name = 'userprofile'
urlpatterns = [
    url(r'^$', views.userprofile, name='userprofile'),
    url(r'^upload/', views.profile_image_upload, name='profile_image_upload'),
]
