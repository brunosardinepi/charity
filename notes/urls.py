from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


app_name = 'notes'
urlpatterns = [
    url(r'^abuse/comment/(?P<comment_pk>\d+)/$', login_required(views.AbuseComment.as_view()), name='abuse_comment'),
    url(r'^abuse/image/(?P<type>[\w-]+)/(?P<image_pk>\d+)/$', login_required(views.AbuseImage.as_view()), name='abuse_image'),

    url(r'^error/amount/none/$', views.error_amount_is_none, name='error_amount_is_none'),
    url(r'^error/campaign/does-not-exist/$', views.error_campaign_does_not_exist, name='error_campaign_does_not_exist'),
    url(r'^error/campaign/vote-participants/$', views.error_campaign_vote_participants, name='error_campaign_vote_participants'),
    url(r'^error/image/size/$', views.error_image_size, name='error_image_size'),
    url(r'^error/image/type/$', views.error_image_type, name='error_image_type'),
    url(r'^error/invite/user-exists/$', views.error_invite_user_exists, name='error_invite_user_exists'),
    url(r'^error/page/does-not-exist/$', views.error_page_does_not_exist, name='error_page_does_not_exist'),
    url(r'^error/password/reset/expired/$', views.error_forgotpasswordreset_expired, name='error_forgotpasswordreset_expired'),
    url(r'^error/password/reset/completed/$', views.error_forgotpasswordreset_completed, name='error_forgotpasswordreset_completed'),
    url(r'^error/permissions/$', views.error_permissions, name='error_permissions'),
    url(r'^error/invalid-request/$', views.error_stripe_invalid_request, name='error_stripe_invalid_request'),
]
