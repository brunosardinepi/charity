from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from . import models
from page.models import Page

import unittest


class DonationTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword'
        )
        self.user.userprofile.first_name = 'John'
        self.user.userprofile.last_name = 'Doe'
        self.user.userprofile.birthday = '1990-01-07'
        self.user.save()

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )

        self.donation = models.Donation.objects.create(
            amount=2000,
            comment='I donated!',
            page=self.page,
            user=self.user
        )

    def test_donation_exists(self):
        donations = models.Donation.objects.all()
        self.assertIn(self.donation, donations)

    def test_donation_creation_time(self):
        donation = models.Donation.objects.create(amount='4000', page=self.page, user=self.user)
        now = timezone.now()
        self.assertLess(donation.date, now)

    def test_donate_page(self):
        response = self.client.get('/%s/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "%s %s" % (self.user.userprofile.first_name, self.user.userprofile.last_name), status_code=200)
        self.assertContains(response, self.donation.comment, status_code=200)
        self.assertContains(response, "$%s" % int(self.donation.amount / 100), status_code=200)
