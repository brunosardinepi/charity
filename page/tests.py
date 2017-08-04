import django

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase

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

        self.page = models.Page.objects.create(
                                                name='Test Page',
                                                description='This is a description for Test Page.',
                                                donation_count='5',
                                                donation_money='100'
                                                )

        self.campaign = CampaignModels.Campaign.objects.create(
                                            name='Test Campaign',
                                            page=self.page,
                                            description='This is a description for Test Campaign.',
                                            donation_count='5',
                                            donation_money='100'
                                            )

        self.campaign2 = CampaignModels.Campaign.objects.create(
                                            name='Another One',
                                            page=self.page,
                                            description='My cat died yesterday',
                                            donation_count='7',
                                            donation_money='60'
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
        self.assertContains(response, self.campaign, status_code=200)
        self.assertContains(response, self.campaign2, status_code=200)

    def test_page_status_logged_in(self):
        """
        Page returns HTTP 200
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-out user
        request.user = self.user

        # test the view
        response = views.page(request, self.page.page_slug)

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count, status_code=200)
        self.assertContains(response, self.page.donation_money, status_code=200)
        self.assertContains(response, self.campaign, status_code=200)
        self.assertContains(response, self.campaign2, status_code=200)
