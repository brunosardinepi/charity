from django.conf.urls import url

from . import views

app_name = 'notes'
urlpatterns = [
    url(r'^error/amount/none/$', views.error_amount_is_none, name='error_amount_is_none'),
    url(r'^error/image/size/$', views.error_image_size, name='error_image_size'),
    url(r'^error/image/type/$', views.error_image_type, name='error_image_type'),
    url(r'^error/invite/user-exists/$', views.error_invite_user_exists, name='error_invite_user_exists'),
    url(r'^error/password/reset/expired/$', views.error_forgotpasswordreset_expired, name='error_forgotpasswordreset_expired'),
    url(r'^error/password/reset/completed/$', views.error_forgotpasswordreset_completed, name='error_forgotpasswordreset_completed'),
    url(r'^error/invalid-request/(?P<error_pk>\d+)/$', views.error_stripe_invalid_request, name='error_stripe_invalid_request'),
]
