from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from . import views
from page.models import Page


class SearchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
                        username='testuser',
                        email='test@test.test',
                        password='testpassword',
                        )

        self.page = Page.objects.create(
                                    name='Test Page',
                                    description='This is a description for Test Page.',
                                    category='Animal',
                                    is_sponsored=True
                                    )

        self.page2 = Page.objects.create(
                                    name='Nachos',
                                    description='I like nachos.',
                                    category='Environment',
                                    is_sponsored=False
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

    def test_search_q_logged_in(self):
        """Results return correctly"""
        request = self.client.get(reverse('search:results'), {'q': 'test'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(request.status_code, 200)
        self.assertContains(request, self.page.name, status_code=200)
        self.assertNotContains(request, self.page2.name, status_code=200)

    def test_search_f_logged_in(self):
        """Results return correctly"""
        request = self.client.get(reverse('search:results'), {'f': 'Environment'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(request.status_code, 200)
        self.assertContains(request, self.page2.name, status_code=200)
        self.assertNotContains(request, self.page.name, status_code=200)

    def test_search_qf_logged_in(self):
        """Results return correctly"""
        request = self.client.get(reverse('search:results'), {'q': 'test', 'f': 'Animal'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(request.status_code, 200)
        self.assertContains(request, self.page.name, status_code=200)
        self.assertNotContains(request, self.page2.name, status_code=200)

