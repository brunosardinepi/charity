from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from . import models
from campaign.models import Campaign
from page.models import Page

import unittest


class DonationTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
            first_name = 'John',
            last_name = 'Doe'
        )
        self.user.userprofile.birthday = '1990-01-07'
        self.user.save()

        self.user2 = User.objects.create_user(
            username='packetloss',
            email='got@no.ping',
            password='plshelap',
            first_name = 'Packets',
            last_name = 'Gone'
        )
        self.user2.userprofile.birthday = '1967-03-12'
        self.user2.save()

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='campaignslug',
            page=self.page,
            type='Event',
            city='Dallas',
            state='Texas',
            description='This is a description for Test Campaign.',
            goal='666',
            donation_count='5',
            donation_money='100'
        )

        self.donation = models.Donation.objects.create(
            amount=2000,
            comment='I donated!',
            page=self.page,
            user=self.user
        )

        self.donation2 = models.Donation.objects.create(
            amount=3500,
            comment='Get good.',
            page=self.page,
            user=self.user
        )

        self.donation3 = models.Donation.objects.create(
            amount=6000,
            comment='I am rich.',
            page=self.page,
            user=self.user2
        )

        self.donation4 = models.Donation.objects.create(
            amount=800,
            comment='I like campaigns.',
            page=self.page,
            campaign=self.campaign,
            user=self.user
        )

    def test_donation_exists(self):
        donations = models.Donation.objects.all()
        self.assertIn(self.donation, donations)
        self.assertIn(self.donation2, donations)
        self.assertIn(self.donation3, donations)
        self.assertIn(self.donation4, donations)

    def test_donation_creation_time(self):
        donation = models.Donation.objects.create(amount='4000', page=self.page, user=self.user)
        now = timezone.now()
        self.assertLess(donation.date, now)

    def test_donate_page(self):
        response = self.client.get('/%s/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "%s %s" % (self.user.first_name, self.user.last_name), status_code=200)
        self.assertContains(response, "%s %s" % (self.user2.first_name, self.user2.last_name), status_code=200)
        self.assertContains(response, self.donation.comment, status_code=200)
        self.assertContains(response, self.donation2.comment, status_code=200)
        self.assertContains(response, "$%s" % int(self.donation.amount / 100), status_code=200)
        self.assertContains(response, "$%s" % int(self.donation2.amount / 100), status_code=200)
        self.assertContains(response, "$%s - %s %s" % (int((self.donation.amount + self.donation2.amount + self.donation4.amount) / 100), self.user.first_name, self.user.last_name), status_code=200)
        self.assertContains(response, "$%s - %s %s" % (int(self.donation3.amount / 100), self.user2.first_name, self.user2.last_name), status_code=200)
        self.assertContains(response, "$%s" % int(self.donation4.amount / 100), status_code=200)
        self.assertContains(response, 'via <a href="/%s/%s/%s/">%s</a>' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug, self.campaign.name), status_code=200)

    def test_donate_campaign(self):
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "$%s" % int(self.donation4.amount / 100), status_code=200)
        self.assertContains(response, self.donation4.comment, status_code=200)
        self.assertContains(response, "$%s - %s %s" % (int(self.donation4.amount / 100), self.user.first_name, self.user.last_name), status_code=200)
