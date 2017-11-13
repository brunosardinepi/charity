from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


app_name = 'votes'
urlpatterns = [
    url(r'^vote/$', login_required(views.VoteView.as_view()), name='vote'),
]
