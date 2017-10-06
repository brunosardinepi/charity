from django.conf.urls import url

from . import views


app_name = 'userprofile'
urlpatterns = [
    url(r'^card/update/', views.update_card, name='update_card'),
    url(r'^upload/', views.profile_image_upload, name='profile_image_upload'),
    url(r'^$', views.userprofile, name='userprofile'),
]
