from django.conf.urls import url

from . import views


app_name = 'plans'
urlpatterns = [
    url(r'^delete/', views.delete_plan, name='delete_plan'),
]

