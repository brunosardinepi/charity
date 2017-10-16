from django.conf.urls import url

from . import views


app_name = 'donation'
urlpatterns = [
    url(r'^card/default/', views.default_card, name='default_card'),
]

