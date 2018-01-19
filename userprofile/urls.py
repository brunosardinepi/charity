from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


app_name = 'userprofile'
urlpatterns = [
    url(r'^billing/$', login_required(views.Billing.as_view()), name='billing'),
    url(r'^card/add/$', views.add_card, name='add_card'),
    url(r'^card/update/$', views.update_card, name='update_card'),
    url(r'^card/list/$', views.card_list, name='card_list'),
    url(r'^donations/$', login_required(views.Donations.as_view()), name='donations'),
    url(r'^images/$', login_required(views.UserImageUpload.as_view()), name='user_image_upload'),
    url(r'^image/(?P<image_pk>\d+)/delete/$', views.user_image_delete, name='user_image_delete'),
    url(r'^image/(?P<image_pk>\d+)/profile-picture/$', views.user_profile_update, name='user_profile_update'),
    url(r'^invitations/$', login_required(views.PendingInvitations.as_view()), name='pending_invitations'),
    url(r'^notifications/$', login_required(views.Notifications.as_view()), name='notifications'),
    url(r'^taxes/$', login_required(views.UserProfileTaxes.as_view()), name='userprofile_taxes'),
    url(r'^pages-and-campaigns/$', login_required(views.PagesCampaigns.as_view()), name='pages_campaigns'),
    url(r'^$', views.userprofile, name='userprofile'),
]
