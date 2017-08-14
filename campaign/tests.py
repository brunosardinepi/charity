import django

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase

from . import forms
from . import models
from . import views
from page.models import Page


class CampaignTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword'
        )

        self.page = Page.objects.create(name='Test Page',)
        self.page.admins.add(self.user.userprofile)

        self.campaign = models.Campaign.objects.create(
            name='Test Campaign',
            page=self.page,
            description='This is a description for Test Campaign.',
            goal='666',
            donation_count='5',
            donation_money='100'
        )

    def test_campaign_exists(self):
        campaigns = models.Campaign.objects.all()
        self.assertIn(self.campaign, campaigns)

    def test_campaign_status_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.campaign(request, self.page.page_slug, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)

    def test_campaign_status_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign(request, self.page.page_slug, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)

    def test_deletecampaignform(self):
        form = forms.DeleteCampaignForm({
            'name': self.campaign
        })
        self.assertTrue(form.is_valid())

    def test_delete_campaign(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_delete(request, self.page.page_slug, self.campaign.campaign_slug)

        self.assertContains(response, self.campaign.name, status_code=200)
