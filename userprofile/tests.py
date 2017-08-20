from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from . import forms
from . import views
from page.models import Page
from campaign.models import Campaign


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

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            user=self.user,
            page=self.page,
            type='Event',
            description='This is a description for Test Campaign.',
            goal='666',
            donation_count='5',
            donation_money='100'
        )

    def test_user_exists(self):
        users = User.objects.all()
        self.assertIn(self.user, users)

    def test_userprofile_page(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.userprofile(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.userprofile.subscribers.get(id=self.page.pk).name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_userprofileform(self):
        form = forms.UserProfileForm({
            'user': self.user,
            'first_name': 'Blanket',
            'last_name': 'Towel',
            'zipcode': 99999
        })
        self.assertTrue(form.is_valid())

    def test_userprofileform_blank(self):
        form = forms.UserProfileForm({})
        self.assertTrue(form.is_valid())
