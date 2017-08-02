from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from . import views


class ProfileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        # create a test user
        self.user = User.objects.create_user(
                        username='testuser',
                        email='test@test.test',
                        password='testpassword',
                        )
        self.user.profile.first_name = 'John'
        self.user.profile.last_name = 'Doe'
        self.user.profile.zipcode = '88888'

    def test_profile_page(self):
        """
        Profile page contains the correct information
        """

        # create an instance of a GET request
        request = self.factory.get('home')

        # simulate a logged-in user
        request.user = self.user

        # test the view
        response = views.profile(request)

        # make sure the user's information is on the page
        self.assertContains(response, self.user.profile.first_name, status_code=200)
        self.assertContains(response, self.user.profile.last_name, status_code=200)
        self.assertContains(response, self.user.profile.zipcode, status_code=200)
