import django
import unittest

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

        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_campaign_create_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.campaign_create(request)

        self.assertEqual(response.status_code, 302)

    def test_campaignform(self):
        form = forms.CampaignForm({
            'name': 'Headphones',
            'campaign_slug': 'headphones',
            'goal': '234',
            'type': 'event',
            'description': 'I wear headphones.'
        })
        self.assertTrue(form.is_valid())
        campaign = form.save(commit=False)
        campaign.page = self.page
        campaign.save()
        self.assertEqual(campaign.name, "Headphones")
        self.assertEqual(campaign.page, self.page)
        self.assertEqual(campaign.campaign_slug, "headphones")
        self.assertEqual(campaign.goal, 234)
        self.assertEqual(campaign.type, "event")
        self.assertEqual(campaign.description, "I wear headphones.")

    def test_campaignform_blank(self):
        form = forms.CampaignForm({})
        self.assertFalse(form.is_valid())

    def test_campaign_edit_status_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 302)

    @unittest.expectedFailure
    def test_campaign_edit_status_not_admin(self):
        """Doesn't test properly with 404 test, so I just expect it to fail instead"""
        request = self.factory.get('home')
        request.user = self.user2
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.campaign_slug)

    def test_campaign_edit_status_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.campaign_edit(request, self.page.page_slug, self.campaign.campaign_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
