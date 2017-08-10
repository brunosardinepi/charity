from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from . import views
from page.models import Page


class UserProfileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        # create a test user
        self.user = User.objects.create_user(
                        username='testuser',
                        email='test@test.test',
                        password='testpassword',
                        )
        self.user.userprofile.first_name = 'John'
        self.user.userprofile.last_name = 'Doe'
        self.user.userprofile.zipcode = '88888'

        # create a test page
        self.page = Page.objects.create(name="Buffalo")

        # subscribe user to page
        self.page.subscribers.add(self.user.userprofile)

    def test_user_exists(self):
        """
        Test user exists
        """

        # get queryset that contains all players
        users = User.objects.all()

        # make sure the test user exists in the queryset
        self.assertIn(self.user, users)

    def test_userprofile_page(self):
        """
        User profile page is accessible
        """

        # create GET request
        request = self.factory.get('home')

        # simulate logged-out user
        request.user = self.user

        # test the view
        response = views.userprofile(request)

        # check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.userprofile.subscribers.get(id=self.page.pk).name, status_code=200)
