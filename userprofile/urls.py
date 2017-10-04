from django.conf.urls import url

from . import views


app_name = 'userprofile'
urlpatterns = [
    url(r'^$', views.userprofile, name='userprofile'),
    url(r'^upload/', views.profile_image_upload, name='profile_image_upload'),
    url(r'^image/delete/', views.user_image_delete, name='user_image_delete'),
    url(r'^image/update/', views.user_profile_update, name='user_profile_update'),
]
