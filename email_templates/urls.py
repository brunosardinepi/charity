from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


app_name = 'email_templates'
urlpatterns = [
    url(r'^(?P<email_pk>\d+)/', views.EmailDetail.as_view(), name='email_detail'),
    url(r'^$', views.EmailList.as_view(), name='email_list'),
]

