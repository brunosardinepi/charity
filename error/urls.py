from django.conf.urls import url

from . import views


app_name = 'error'
urlpatterns = [
    url(r'^image/size/$', views.error_image_size, name='error_image_size'),
    url(r'^invite/user-exists/$', views.error_invite_user_exists, name='error_invite_user_exists'),
]
