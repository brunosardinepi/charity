from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


app_name = 'notes'
urlpatterns = [
    url(r'^abuse/comment/(?P<comment_pk>\d+)/$', login_required(views.AbuseComment.as_view()), name='abuse_comment'),
    url(r'^abuse/image/(?P<type>[\w-]+)/(?P<image_pk>\d+)/$', login_required(views.AbuseImage.as_view()), name='abuse_image'),

    url(r'^error/amount/none/$', views.error_amount_is_none, name='error_amount_is_none'),
    url(r'^error/campaign/vote-participants/$', views.error_campaign_vote_participants, name='error_campaign_vote_participants'),
    url(r'^error/image/size/$', views.error_image_size, name='error_image_size'),
    url(r'^error/image/type/$', views.error_image_type, name='error_image_type'),
    url(r'^error/invite/user-exists/$', views.error_invite_user_exists, name='error_invite_user_exists'),
    url(r'^error/password/reset/expired/$', views.error_forgotpasswordreset_expired, name='error_forgotpasswordreset_expired'),
    url(r'^error/password/reset/completed/$', views.error_forgotpasswordreset_completed, name='error_forgotpasswordreset_completed'),
    url(r'^error/invalid-request/(?P<error_pk>\d+)/$', views.error_stripe_invalid_request, name='error_stripe_invalid_request'),
]
