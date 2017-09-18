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
            page_slug='testpage',
            city='San Diego',
            state='CA',
            description='This is a description for Test Page. test test test test test test',
            category='Animal',
            is_sponsored=True
        )

        self.page2 = Page.objects.create(
            name='Nachos',
            page_slug='mmmmmmmm',
            city='Seattle',
            state='WA',
            description='I like nachos. nachos nachos nachos',
            category='Environment',
            is_sponsored=False
        )

    def test_search_page_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('search:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_page_logged_out(self):
        response = self.client.get(reverse('search:search'))
        self.assertEqual(response.status_code, 200)
