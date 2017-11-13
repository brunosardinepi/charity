from django.conf.urls import url

from . import views


app_name = 'faqs'
urlpatterns = [
    url(r'^$', views.FAQList.as_view(), name='faq_list'),
]
