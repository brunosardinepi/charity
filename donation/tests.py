import datetime
import pytz

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from . import models
from .forms import BaseDonate
from campaign.models import Campaign, VoteParticipant
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
            category='Animal',
            stripe_verified=True,
        )

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='campaignslug',
            page=self.page,
            type='vote',
            description='This is a description for Test Campaign.',
            goal='666',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.campaign2 = Campaign.objects.create(
            name='My Phone',
            campaign_slug='myphone',
            page=self.page,
            type='general',
            description='There it is on the table',
            goal='123',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
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

        self.donation5 = models.Donation.objects.create(
            amount=999,
            anonymous_donor=True,
            comment='Hiding my name',
            page=self.page,
            user=self.user
        )

        self.donation6 = models.Donation.objects.create(
            amount=723,
            anonymous_amount=True,
            comment='Cant see my amount',
            page=self.page,
            user=self.user
        )

        self.donation7 = models.Donation.objects.create(
            amount=163,
            anonymous_amount=True,
            anonymous_donor=True,
            comment='Total ghost',
            page=self.page,
            user=self.user
        )

        self.donation8 = models.Donation.objects.create(
            amount=1375,
            anonymous_donor=True,
            comment='No name',
            page=self.page,
            campaign=self.campaign,
            user=self.user
        )

        self.donation9 = models.Donation.objects.create(
            amount=5665,
            anonymous_amount=True,
            comment='Goodbye amount',
            page=self.page,
            campaign=self.campaign,
            user=self.user
        )

        self.donation10 = models.Donation.objects.create(
            amount=8365,
            anonymous_amount=True,
            anonymous_donor=True,
            comment='What is happening',
            page=self.page,
            campaign=self.campaign,
            user=self.user
        )

        self.vote_participant = VoteParticipant.objects.create(
            name="Harry",
            campaign=self.campaign,
        )

        self.vote_participant2 = VoteParticipant.objects.create(
            name="Sally",
            campaign=self.campaign,
        )

    def test_donation_exists(self):
        donations = models.Donation.objects.all()
        self.assertIn(self.donation, donations)
        self.assertIn(self.donation2, donations)
        self.assertIn(self.donation3, donations)
        self.assertIn(self.donation4, donations)
        self.assertIn(self.donation5, donations)
        self.assertIn(self.donation6, donations)
        self.assertIn(self.donation7, donations)

    def test_donation_creation_time(self):
        donation = models.Donation.objects.create(amount='4000', page=self.page, user=self.user)
        now = timezone.now()
        self.assertLess(donation.date, now)

    def test_donations_page(self):
        response = self.client.get('/%s/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "%s %s" % (self.user.first_name, self.user.last_name))
        self.assertContains(response, "%s %s" % (self.user2.first_name, self.user2.last_name))
        self.assertContains(response, self.donation.comment)
        self.assertContains(response, self.donation2.comment)
        self.assertContains(response, "$%s" % int(self.donation.amount / 100))
        self.assertContains(response, "$%s" % int(self.donation2.amount / 100))
        self.assertContains(response, "{} {}".format(self.user.first_name, self.user.last_name))
        self.assertContains(response, "${}".format(int((self.donation.amount + self.donation2.amount + self.donation4.amount) / 100)))
        self.assertContains(response, "${}".format(int(self.donation3.amount / 100), self.user2.first_name, self.user2.last_name))
        self.assertContains(response, "{} {}".format(self.user2.first_name, self.user2.last_name))
        self.assertContains(response, "$%s" % int(self.donation4.amount / 100), status_code=200)
        self.assertContains(response, 'via the <a href="/%s/%s/%s/">%s</a> Campaign' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug, self.campaign.name))
        self.assertContains(response, "${}".format(int(self.donation5.amount / 100)))
        self.assertNotContains(response, "${}".format(int(self.donation6.amount / 100)))
        self.assertContains(response, "An anonymous donor")
        self.assertContains(response, "an anonymous amount")

    def test_donations_campaign(self):
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "$%s" % int(self.donation4.amount / 100), status_code=200)
        self.assertContains(response, self.donation4.comment, status_code=200)
        self.assertContains(response, "{} {}".format(self.donation4.user.first_name, self.donation4.user.last_name))
        self.assertContains(response, "${}".format(int(self.donation8.amount / 100)))
        self.assertContains(response, "An anonymous donor")
        self.assertContains(response, "an anonymous amount")

    def test_donate_page(self):
        response = self.client.get('/{}/donate/'.format(self.page.page_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name)

    def test_donate_campaign(self):
        response = self.client.get('/{}/{}/{}/'.format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.vote_participant.name)
        self.assertContains(response, self.vote_participant2.name)

        response = self.client.get('/{}/{}/{}/donate/'.format(self.page.page_slug, self.campaign2.pk, self.campaign2.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name)
        self.assertContains(response, self.campaign2.name)
        self.assertNotContains(response, "Your vote is for")

        response = self.client.get('/{}/{}/{}/donate/{}/'.format(self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug, self.vote_participant.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name)
        self.assertContains(response, self.campaign.name)
        self.assertContains(response, 'Your vote is for: <span class="font-weight-bold">{}</span>'.format(self.vote_participant.name))
        self.assertNotContains(response, 'Your vote is for: <span class="font-weight-bold">{}</span>'.format(self.vote_participant2.name))

    def test_donateform_bad_amount(self):
        form = BaseDonate({
            'amount': 1000000,
        })
        self.assertFalse(form.is_valid())

    def test_donateform_good_amount(self):
        form = BaseDonate({
            'amount': 999999,
        })
        self.assertTrue(form.is_valid())
