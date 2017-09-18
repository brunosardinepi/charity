from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from . import forms
from . import views
from invitations.models import ManagerInvitation
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
        self.user.userprofile.state = 'Kansas'

        self.page = Page.objects.create(name="Buffalo")
        self.page2 = Page.objects.create(name="Remote")
        self.page3 = Page.objects.create(name="Foot")
        self.page.subscribers.add(self.user.userprofile)
        self.page.managers.add(self.user.userprofile)
        self.page2.admins.add(self.user.userprofile)

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            page=self.page,
            type='Event',
            description='This is a description for Test Campaign.',
            goal='666',
            donation_count='5',
            donation_money='100'
        )

        self.campaign.campaign_admins.add(self.user.userprofile)

        self.invitation = ManagerInvitation.objects.create(
            invite_to="rupert@oi.mate",
            invite_from=self.user,
            page=self.page,
            manager_edit=True,
            manager_delete=True,
            manager_invite=True
        )

    def test_user_exists(self):
        users = User.objects.all()
        self.assertIn(self.user, users)

    def test_userprofile_page(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.userprofile.subscribers.get(id=self.page.pk).name, status_code=200)
        self.assertContains(response, self.user.userprofile.state, status_code=200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.page2.name, status_code=200)
        self.assertNotContains(response, self.page3.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)

    def test_userprofileform(self):
        form = forms.UserProfileForm({
            'user': self.user,
            'first_name': 'Blanket',
            'last_name': 'Towel',
            'state': 'KS'
        })
        self.assertTrue(form.is_valid())

    def test_userprofileform_blank(self):
        form = forms.UserProfileForm({})
        self.assertFalse(form.is_valid())

    def test_sent_invitations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/')

        self.assertContains(response, "rupert@oi.mate", status_code=200)

        self.invitation.expired = True
        self.invitation.save()

        response = self.client.get('/profile/')
        self.assertNotContains(response, "rupert@oi.mate", status_code=200)

    def test_image_upload(self):
        self.client.login(username='testuser', password='testpassword')
        with open('media/tests/up.png', 'rb') as image:
            response = self.client.post('/profile/', {'state': 'FL', 'avatar': image})
        self.assertRedirects(response, '/profile/', 302, 200)
        response = self.client.get('/profile/')
        self.assertContains(response, 'media/up', status_code=200)

    def test_image_upload_error_size(self):
        self.client.login(username='testuser', password='testpassword')
        with open('media/tests/error_image_size.jpg', 'rb') as image:
            response = self.client.post('/profile/', {'state': 'AL', 'avatar': image})
        self.assertRedirects(response, '/error/image/size/', 302, 200)

    def test_image_upload_error_type(self):
        self.client.login(username='testuser', password='testpassword')
        with open('media/tests/error_image_type.txt', 'rb') as image:
            response = self.client.post('/profile/', {'state': 'AL', 'avatar': image})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload a valid image. The file you uploaded was either not an image or a corrupted image.", status_code=200)
