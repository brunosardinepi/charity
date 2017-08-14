from django.conf.urls import url, include
from django.contrib import admin

from . import views
from page import views as PageViews
from campaign import views as CampaignViews


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/', views.LoginView.as_view(), name='login'),
    url(r'^accounts/signup/', views.SignupView.as_view(), name='signup'),
    url(r'^accounts/password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^profile/', include('userprofile.urls', namespace='userprofile')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^subscribe/(?P<page_pk>\d+)/(?P<action>[\w-]*)/$', PageViews.subscribe, name='subscribe'),
    url(r'^(?P<page_slug>[\w-]+)/c/(?P<campaign_slug>[\w-]+)/$', CampaignViews.campaign, name='campaign'),
    url(r'^create/$', PageViews.page_create, name='page_create'),
    url(r'^(?P<page_slug>[\w-]+)/edit/$', PageViews.page_edit, name='page_edit'),
    url(r'^(?P<page_slug>[\w-]+)/delete/$', PageViews.page_delete, name='page_delete'),
    url(r'^(?P<page_slug>[\w-]+)/$', PageViews.page, name='page'),
    url(r'^$', views.home, name='home'),
]
