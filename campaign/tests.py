import django

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase

from . import views
from . import models
from page import models as PageModels


class CampaignTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
                                            username='testuser',
                                            email='test@test.test',
                                            password='testpassword'
                                            )

        self.page = PageModels.Page.objects.create(
                                        name='Test Page',
                                        )

        self.campaign = models.Campaign.objects.create(
                                            name='Test Campaign',
                                            page=self.page,
                                            description='This is a description for Test Campaign.',
                                            goal='666',
                                            donation_count='5',
                                            donation_money='100'
                                            )

    def test_campaign_exists(self):
        """
        Test campaign exists
        """

        # get queryset that contains all campaigns
        campaigns = models.Campaign.objects.all()

        # make sure the test campaign exists in the queryset
        self.assertIn(self.campaign, campaigns)

    def test_campaign_status_logged_out(self):
        """
        Campaign page returns HTTP 200
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-out user
        request.user = AnonymousUser()

        # test the view
        response = views.campaign(request, self.page.page_slug, self.campaign.campaign_slug)

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)

    def test_campaign_status_logged_in(self):
        """
        Campaign page returns HTTP 200
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-out user
        request.user = self.user

        # test the view
        response = views.campaign(request, self.page.page_slug, self.campaign.campaign_slug)

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.description, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, self.campaign.donation_count, status_code=200)
        self.assertContains(response, self.campaign.donation_money, status_code=200)
