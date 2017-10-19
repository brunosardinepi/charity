from django.conf.urls import url

from . import views


app_name = 'webhooks'
urlpatterns = [
    url(r'^charge-succeeded/', views.charge_succeeded, name='charge_succeeded'),
]

