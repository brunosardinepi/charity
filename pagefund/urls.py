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
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_slug>[\w-]+)/', CampaignViews.campaign, name='campaign'),
    url(r'^(?P<page_slug>[\w-]+)/', PageViews.page, name='page'),
    url(r'^$', views.home, name='home'),
]
