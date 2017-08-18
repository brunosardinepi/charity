from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from . import views
from page.models import Page


class UserProfileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
        )
        self.user.userprofile.first_name = 'John'
        self.user.userprofile.last_name = 'Doe'
        self.user.userprofile.zipcode = '88888'

        self.page = Page.objects.create(name="Buffalo")
        self.page.subscribers.add(self.user.userprofile)

    def test_user_exists(self):
        users = User.objects.all()
        self.assertIn(self.user, users)

    def test_userprofile_page(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.userprofile(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.userprofile.subscribers.get(id=self.page.pk).name, status_code=200)
