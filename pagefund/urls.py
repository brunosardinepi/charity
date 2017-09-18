from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
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
    url(r'^invite/', include('invitations.urls', namespace='invitations')),
    url(r'^subscribe/(?P<page_pk>\d+)/(?P<action>[\w-]*)/$', PageViews.subscribe, name='subscribe'),
    url(r'^comments/', include('comments.urls', namespace='comments')),
    url(r'^error/', include('error.urls', namespace='error')),

    url(r'^create/$', PageViews.page_create, name='page_create'),
    url(r'^(?P<page_slug>[\w-]+)/edit/$', PageViews.page_edit, name='page_edit'),
    url(r'^(?P<page_slug>[\w-]+)/delete/$', PageViews.page_delete, name='page_delete'),
    url(r'^(?P<page_slug>[\w-]+)/upload/$', PageViews.page_image_upload, name='page_image_upload'),

    url(r'^(?P<page_slug>[\w-]+)/managers/invite/$', PageViews.page_invite, name='page_invite'),
    url(r'^(?P<page_slug>[\w-]+)/managers/(?P<manager_pk>\d+)/remove/$', PageViews.remove_manager, name='remove_manager'),
    url(r'^(?P<page_slug>[\w-]+)/$', PageViews.page, name='page'),

    url(r'^(?P<page_slug>[\w-]+)/campaign/create/$', CampaignViews.campaign_create, name='campaign_create'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/edit/$', CampaignViews.campaign_edit, name='campaign_edit'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/delete/$', CampaignViews.campaign_delete, name='campaign_delete'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/upload/$', CampaignViews.campaign_image_upload, name='campaign_image_upload'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/managers/invite/$', CampaignViews.campaign_invite, name='campaign_invite'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/managers/(?P<manager_pk>\d+)/remove/$', CampaignViews.remove_manager, name='remove_manager'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/$', CampaignViews.campaign, name='campaign'),

    url(r'^$', views.home, name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
