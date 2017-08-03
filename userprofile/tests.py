from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from . import views


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
