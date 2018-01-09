from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'comments'
urlpatterns = [
    url(r'^post/(?P<content_type>\d+)/(?P<object_id>\d+)/',
        login_required(views.CommentPost.as_view()),
        name='comment_post'),
]
