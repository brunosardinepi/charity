from django.conf.urls import url

from . import views


app_name = 'webhooks'
urlpatterns = [
    url(r'^charge-succeeded/', views.charge_succeeded, name='charge_succeeded'),
    url(r'^customer-subscription-created/', views.customer_subscription_created, name='customer_subscription_created'),
]

