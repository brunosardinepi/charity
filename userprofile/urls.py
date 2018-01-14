from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


app_name = 'userprofile'
urlpatterns = [
    url(r'^card/add/$', views.add_card, name='add_card'),
    url(r'^card/update/$', views.update_card, name='update_card'),
    url(r'^card/list/$', views.card_list, name='card_list'),
    url(r'^images/$', login_required(views.UserImageUpload.as_view()), name='user_image_upload'),
    url(r'^image/(?P<image_pk>\d+)/delete/$', views.user_image_delete, name='user_image_delete'),
    url(r'^image/(?P<image_pk>\d+)/profile-picture/$', views.user_profile_update, name='user_profile_update'),
    url(r'^notifications/update/$', views.update_notification_preferences, name='update_notification_preferences'),
    url(r'^taxes/$', login_required(views.UserProfileTaxes.as_view()), name='userprofile_taxes'),
    url(r'^$', views.userprofile, name='userprofile'),
]
