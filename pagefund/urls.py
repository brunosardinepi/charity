from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import config
from . import views
from campaign import views as CampaignViews
from invitations import views as InvitationsViews
from page.forms import PageForm1, PageForm2, PageForm3, PageForm4, PageForm5
from page import views as PageViews


FORMS = [("Organization", PageForm1),
         ("Personal", PageForm2),
         ("EIN", PageForm3),
         ("Bank", PageForm4),
         ("Review", PageForm5)]

urlpatterns = [
    url(r'^{}/'.format(config.settings['admin']), admin.site.urls),
    url(r'^accounts/email/', TemplateView.as_view(template_name='404.html')),
    url(r'^accounts/login/', views.LoginView.as_view(), name='login'),
    url(r'^accounts/signup/', views.SignupView.as_view(), name='signup'),
    url(r'^accounts/social/connections/', views.ConnectionsView.as_view(), name='socialaccount_connections'),
    url(r'^accounts/social/signup/', views.SocialSignupView.as_view(), name='social_signup'),
    url(r'^accounts/confirm-email/$', views.EmailVerificationSentView.as_view(), name='email_verification_sent'),
    url(r"^accounts/confirm-email/(?P<key>[-:\w]+)/$", views.ConfirmEmailView.as_view(), name='account_confirm_email'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^profile/', include('userprofile.urls', namespace='userprofile')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^invite/$', views.invite, name='invite'),
    url(r'^invite/', include('invitations.urls', namespace='invitations')),
    url(r'^comments/', include('comments.urls', namespace='comments')),
    url(r'^donation/', include('donation.urls', namespace='donation')),
    url(r'^password/forgot/$', InvitationsViews.forgot_password_request, name='forgot_password_request'),
    url(r'^password/change/$', InvitationsViews.change_password_request, name='change_password_request'),
    url(r'^password/reset/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', InvitationsViews.forgot_password_reset, name='forgot_password_reset'),
    url(r'^webhooks/', include('webhooks.urls', namespace='webhooks')),
    url(r'^plans/', include('plans.urls', namespace='plans')),
    url(r'^faq/', include('faqs.urls', namespace='faqs')),
    url(r'^about/$', TemplateView.as_view(template_name="about.html")),
    url(r'^terms-of-service/$', TemplateView.as_view(template_name="terms_of_service.html")),
    url(r'^privacy-policy/$', TemplateView.as_view(template_name="privacy_policy.html")),
    url(r'^legal/$', TemplateView.as_view(template_name="legal.html")),
    url(r'^notes/', include('notes.urls', namespace='notes')),
    url(r'^create/$', TemplateView.as_view(template_name="create.html")),
    url(r'^features/$', TemplateView.as_view(template_name="features.html")),
    url(r'^email-templates/', include('email_templates.urls', namespace='email_templates')),

    url(r'^page/subscribe/(?P<page_pk>\d+)/$', PageViews.subscribe, name='subscribe'),
    url(r'^create/page/$', login_required(PageViews.PageWizard.as_view(
        FORMS,
        condition_dict={ 'EIN': PageViews.show_message_form_condition })),
        name='page_create'),
    url(r'^(?P<page_slug>[\w-]+)/edit/bank/$', login_required(PageViews.PageEditBankInfo.as_view()), name='page_edit_bank_info'),
    url(r'^(?P<page_slug>[\w-]+)/edit/$', PageViews.page_edit, name='page_edit'),
    url(r'^(?P<page_slug>[\w-]+)/campaigns/$', PageViews.PageCampaigns.as_view(), name='page_campaigns'),
    url(r'^(?P<page_slug>[\w-]+)/donations/$', PageViews.PageDonations.as_view(), name='page_donations'),
    url(r'^(?P<page_slug>[\w-]+)/manage/analytics/$', login_required(PageViews.PageDashboardAnalytics.as_view()), name='page_dashboard_analytics'),
    url(r'^(?P<page_slug>[\w-]+)/manage/admin/$', login_required(PageViews.PageDashboardAdmin.as_view()), name='page_dashboard_admin'),
    url(r'^(?P<page_slug>[\w-]+)/manage/donations/$', login_required(PageViews.PageDashboardDonations.as_view()), name='page_dashboard_donations'),
    url(r'^(?P<page_slug>[\w-]+)/manage/campaigns/$', login_required(PageViews.PageDashboardCampaigns.as_view()), name='page_dashboard_campaigns'),
    url(r'^(?P<page_slug>[\w-]+)/manage/images/$', login_required(PageViews.PageDashboardImages.as_view()), name='page_dashboard_images'),
    url(r'^page/dashboard/ajax/donations/', PageViews.PageAjaxDonations.as_view(), name='page_ajax_donations'),
    url(r'^(?P<page_slug>[\w-]+)/delete/$', PageViews.page_delete, name='page_delete'),
    url(r'^(?P<page_slug>[\w-]+)/donate/$', PageViews.PageDonate.as_view(), name='page_donate'),
    url(r'^page/image/(?P<image_pk>\d+)/delete/$', PageViews.page_image_delete, name='page_image_delete'),
    url(r'^page/image/(?P<image_pk>\d+)/profile-picture/$', PageViews.page_profile_update, name='page_profile_update'),
    url(r'^(?P<page_slug>[\w-]+)/managers/invite/$', PageViews.page_invite, name='page_invite'),
    url(r'^(?P<page_slug>[\w-]+)/managers/(?P<manager_pk>\d+)/remove/$', PageViews.remove_manager, name='remove_manager'),
    url(r'^(?P<page_slug>[\w-]+)/$', PageViews.page, name='page'),

    url(r'^campaign/subscribe/(?P<campaign_pk>\d+)/$', CampaignViews.subscribe, name='campaign_subscribe'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/donate/(?P<vote_participant_pk>\d+)/$', CampaignViews.CampaignDonate.as_view(), name='campaign_donate'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/donate/$', CampaignViews.CampaignDonate.as_view(), name='campaign_donate'),
    url(r'^create/campaign/$', login_required(CampaignViews.CampaignCreate.as_view()), name='campaign_create'),
    url(r'^create/campaign/search/$', CampaignViews.campaign_search_pages, name='campaign_search_pages'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/vote/edit/$', login_required(CampaignViews.CampaignEditVote.as_view()), name='campaign_edit_vote'),
    url(r'^(?P<page_slug>[\w-]+)/campaign/create/$', login_required(CampaignViews.CampaignCreate.as_view()), name='campaign_create'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/edit/$', CampaignViews.campaign_edit, name='campaign_edit'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/donations/$', CampaignViews.CampaignDonations.as_view(), name='campaign_donations'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/delete/$', CampaignViews.campaign_delete, name='campaign_delete'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/manage/analytics/$', login_required(CampaignViews.CampaignDashboardAnalytics.as_view()), name='campaign_dashboard_analytics'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/manage/admin/$', login_required(CampaignViews.CampaignDashboardAdmin.as_view()), name='campaign_dashboard_admin'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/manage/donations/$', login_required(CampaignViews.CampaignDashboardDonations.as_view()), name='campaign_dashboard_donations'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/manage/images/$', login_required(CampaignViews.CampaignDashboardImages.as_view()), name='campaign_dashboard_images'),
    url(r'^campaign/dashboard/ajax/donations/', CampaignViews.CampaignAjaxDonations.as_view(), name='campaign_ajax_donations'),
    url(r'^campaign/image/(?P<image_pk>\d+)/delete/$', CampaignViews.campaign_image_delete, name='campaign_image_delete'),
    url(r'^campaign/image/(?P<image_pk>\d+)/profile-picture/$', CampaignViews.campaign_profile_update, name='campaign_profile_update'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/managers/invite/$', CampaignViews.campaign_invite, name='campaign_invite'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/managers/(?P<manager_pk>\d+)/remove/$', CampaignViews.remove_manager, name='campaign_remove_manager'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/$', CampaignViews.campaign, name='campaign'),

    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    url(r'^sitemap.xml$', TemplateView.as_view(template_name="sitemap.xml", content_type="application/xml")),
    url(r'^BingSiteAuth.xml$', TemplateView.as_view(template_name="BingSiteAuth.xml", content_type="application/xml")),
    url(r'^google24da7f1b4197f0d1.html$', TemplateView.as_view(template_name="google24da7f1b4197f0d1.html")),

    url(r'^$', views.home, name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# django-debug-toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = views.handler404
handler500 = views.handler500
