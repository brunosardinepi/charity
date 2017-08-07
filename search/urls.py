from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^results/', views.results, name='results'),
    url(r'^$', views.search, name='search'),
]
