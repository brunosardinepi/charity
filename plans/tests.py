from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from .models import StripePlan
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

        self.plan = StripePlan.objects.create(
            amount=2000,
            page=self.page,
            campaign=self.campaign,
            user=self.user,
            stripe_plan_id="plan_adagD87asg2342huif3whluq3qr",
            stripe_subscription_id="sub_Sh2982SKDnjSADioqdn3s",
            interval="month"
        )

        self.plan2 = StripePlan.objects.create(
            amount=6500,
            page=self.page,
            user=self.user2,
            stripe_plan_id="plan_AS8o7tasdASDh23eads254",
            stripe_subscription_id="sub_87sadfZDSHF8o723rhnu23",
            interval="month"
        )

    def test_plan_exists(self):
        plans = StripePlan.objects.all()
        self.assertIn(self.plan, plans)
        self.assertIn(self.plan2, plans)

    def test_plan_creation_time(self):
        plan = StripePlan.objects.create(
            amount=1700,
            page=self.page,user=self.user,
            stripe_plan_id="plan_AS8o7tasdASDh23eads254",
            stripe_subscription_id="sub_87sadfZDSHF8o723rhnu23",
            interval="month"
        )
        now = timezone.now()
        self.assertLess(plan.date, now)

    def test_plan_profile(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recurring Donations", status_code=200)
        self.assertContains(response, "$%s every month to " % int(self.plan.amount / 100), status_code=200)

        self.client.login(username='packetloss', password='plshelap')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recurring Donations", status_code=200)
        self.assertContains(response, "$%s every month to " % int(self.plan2.amount / 100), status_code=200)


