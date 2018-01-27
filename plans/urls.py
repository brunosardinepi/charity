from django.conf.urls import url

from . import views


app_name = 'plans'
urlpatterns = [
    url(r'^/(?P<plan_pk>\d+)/delete/', views.delete_plan, name='delete_plan'),
]

