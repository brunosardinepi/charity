from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase

from . import views


class SearchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
                        username='testuser',
                        email='test@test.test',
                        password='testpassword',
                        )

    def test_search_page_logged_in(self):
        """Search page is accessible when logged in"""
        request = self.factory.get('home')
        request.user = self.user
        response = views.search(request)
        self.assertEqual(response.status_code, 200)

    def test_search_page_logged_out(self):
        """Search page is accessible when logged out"""
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.search(request)
        self.assertEqual(response.status_code, 200)
