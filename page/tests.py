import django

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.test import Client, RequestFactory, TestCase

import unittest

from . import views
from . import models
from campaign import models as CampaignModels


class CampaignTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
                                            username='testuser',
                                            email='test@test.test',
                                            password='testpassword'
                                            )

        self.user2 = User.objects.create_user(
                                            username='harrypotter',
                                            email='harry@potter.com',
                                            password='imawizard'
                                            )

        self.page = models.Page.objects.create(
                                                name='Test Page',
                                                description='This is a description for Test Page.',
                                                donation_count='20',
                                                donation_money='30',
                                                category='Animal'
                                                )
        self.page.admins.add(self.user.userprofile)
        self.page.subscribers.add(self.user.userprofile)

        self.campaign = CampaignModels.Campaign.objects.create(
                                            name='Test Campaign',
                                            page=self.page,
                                            description='This is a description for Test Campaign.',
                                            goal='11',
                                            donation_count='21',
                                            donation_money='31'
                                            )

        self.campaign2 = CampaignModels.Campaign.objects.create(
                                            name='Another One',
                                            page=self.page,
                                            description='My cat died yesterday',
                                            goal='12',
                                            donation_count='22',
                                            donation_money='33'
                                            )

    def test_page_exists(self):
        """
        Test page exists
        """

        # get queryset that contains all pages
        pages = models.Page.objects.all()

        # make sure the test page exists in the queryset
        self.assertIn(self.page, pages)

    def test_page_status_logged_out(self):
        """
        Page returns HTTP 200
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-out user
        request.user = AnonymousUser()

        # test the view
        response = views.page(request, self.page.page_slug)

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count, status_code=200)
        self.assertContains(response, self.page.donation_money, status_code=200)
        self.assertContains(response, self.page.category, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign2.goal, status_code=200)
        self.assertContains(response, self.campaign2.donation_money, status_code=200)

    def test_page_status_logged_in(self):
        """
        Page returns HTTP 200
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-in user
        request.user = self.user

        # test the view
        response = views.page(request, self.page.page_slug)

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count, status_code=200)
        self.assertContains(response, self.page.donation_money, status_code=200)
        self.assertContains(response, self.page.category, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign2.goal, status_code=200)
        self.assertContains(response, self.campaign2.donation_money, status_code=200)

    def test_page_edit_status_logged_out(self):
        """
        Page returns HTTP 302 redirect
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-out user
        request.user = AnonymousUser()

        # test the view
        response = views.page_edit(request, self.page.page_slug)

        # check that the response is 302
        self.assertEqual(response.status_code, 302)

    @unittest.expectedFailure
    def test_page_edit_status_not_admin(self):
        """
        Page returns HTTP 404
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-in user
        request.user = self.user2

        # test the view
        response = views.page_edit(request, self.page.page_slug)

    def test_page_edit_status_admin(self):
        """
        Page returns HTTP 200
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-in user
        request.user = self.user

        # test the view
        response = views.page_edit(request, self.page.page_slug)

        # check that the response is 404
        self.assertEqual(response.status_code, 200)

    def test_page_not_subscribed(self):
        """Page returns 'subscribe' button"""

        # create GET request
        request = self.factory.get('home')

        # simulate logged-in user
        request.user = self.user2

        # test the view
        response = views.page(request, self.page.page_slug)

        # check that the response is 200
        self.assertContains(response, 'name="subscribe"', status_code=200)

    def test_page_subscribed(self):
        """Page returns 'unsubscribe' button"""

        # create GET request
        request = self.factory.get('home')

        # simulate logged-in user
        request.user = self.user

        # test the view
        response = views.page(request, self.page.page_slug)

        # check that the response is 200
        self.assertContains(response, 'name="unsubscribe"', status_code=200)

    def test_page_subscribe_redirect(self):
        """Page redirects to signup if you try to subscribe while logged out"""

        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.subscribe(request, self.page.pk, action="subscribe")

        self.assertEqual(response.status_code, 302)
