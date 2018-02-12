import ast
import datetime
import pytz

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase
from django.utils import timezone

from . import forms
from . import models
from . import views
from campaign.models import Campaign
from donation.models import Donation
from invitations.models import ManagerInvitation
from page.models import Page
from pagefund.utils import has_notification


class UserProfileTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
            first_name='John',
            last_name='Doe',
        )
        self.user.userprofile.state = 'Kansas'
        self.user.userprofile.save()

        self.user2 = User.objects.create_user(
            username='penandearbuds',
            email='pen@and.earbuds',
            password='postitnote',
            first_name='Paper',
            last_name='Towels',
        )
        self.user2.userprofile.notification_email_donation = True
        self.user2.userprofile.notification_email_campaign_created = False
        self.user2.userprofile.save()

        self.user3 = User.objects.create_user(
            username='clickthemouse',
            email='click@the.mouse',
            password='leftandright',
            first_name='Space',
            last_name='Heater',
        )

        self.page = Page.objects.create(
            name="Buffalo",
            page_slug="buffalo",
            type="nonprofit",
        )
        self.page2 = Page.objects.create(
            name="Remote",
            page_slug="remote",
        )
        self.page3 = Page.objects.create(
            name="Foot",
            page_slug="foot",
        )
        self.page.subscribers.add(self.user.userprofile)
        self.page.managers.add(self.user.userprofile)
        self.page2.admins.add(self.user.userprofile)

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='testcampaign',
            page=self.page,
            type='Event',
            description='This is a description for Test Campaign.',
            goal='666',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.campaign.campaign_admins.add(self.user.userprofile)

        self.campaign2 = Campaign.objects.create(
            name='Mousepad',
            campaign_slug='mousepad',
            page=self.page2,
            type='Event',
            description='I use a mousepad.',
            goal='15',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.campaign2.campaign_managers.add(self.user.userprofile)

        self.campaign3 = Campaign.objects.create(
            name='Pencil',
            campaign_slug='pencil',
            page=self.page,
            type='Event',
            description='I write with a pencil.',
            goal='153',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.campaign3.campaign_subscribers.add(self.user.userprofile)

        self.invitation = ManagerInvitation.objects.create(
            invite_to="rupert@oi.mate",
            invite_from=self.user,
            page=self.page,
            manager_edit=True,
            manager_delete=True,
            manager_invite=True
        )

        self.donation = Donation.objects.create(
            amount=2200,
            page=self.page,
            user=self.user,
        )

        self.donation2 = Donation.objects.create(
            amount=900,
            page=self.page,
            campaign=self.campaign,
            user=self.user,
        )

        self.card = models.StripeCard.objects.create(
            user=self.user.userprofile,
            name="my card",
            stripe_card_id="cus_jhasdflkuh32ofhqwefslhkj",
            stripe_card_fingerprint="ho87OHDS82d3"
        )

    def test_user_exists(self):
        users = User.objects.all()
        self.assertIn(self.user, users)

    def test_card_exists(self):
        cards = models.StripeCard.objects.all()
        self.assertIn(self.card, cards)

    def test_password_requirements(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
        data = {
            'email': 'test2@test.test',
            'email2': 'test2@test.test',
            'password1': 'dog',
            'password2': 'dog',
        }
        response = self.client.post('/accounts/signup/', data)
        self.assertEqual(response.status_code, 200)
        user = User.objects.filter(email='test2@test.test')
        self.assertEqual(user.count(), 0)

        data['password1'] = 'imadog2'
        data['password2'] = 'imadog2'
        response = self.client.post('/accounts/signup/', data)
        self.assertRedirects(response, '/accounts/confirm-email/', 302, 200)
        user = User.objects.filter(email='test2@test.test')
        self.assertEqual(user.count(), 1)

    def test_userprofile_page(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.userprofile.state, status_code=200)
        self.assertContains(response, "Personal Information")
        self.assertContains(response, "Upload and Edit images")

    def test_billing(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/billing/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved Credit Cards")
        self.assertContains(response, "Add Credit Card")

    def test_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/donations/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recurring Donations")
        self.assertContains(response, "Donations")
        self.assertContains(response, '${}'.format(int(self.donation.amount / 100)))
        self.assertContains(response, self.page.name)
        self.assertContains(response, '${}'.format(int(self.donation2.amount / 100)))
        self.assertContains(response, self.campaign.name)

    def test_pages_campaigns(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/pages-and-campaigns/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Pages")
        self.assertContains(response, "My Campaigns")
        self.assertContains(response, self.user.userprofile.subscribers.get(id=self.page.pk).name, status_code=200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.page2.name, status_code=200)
        self.assertNotContains(response, self.page3.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign3.name, status_code=200)

    def test_userprofileform(self):
        form = forms.UserProfileForm({
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': '1990-09-23',
            'state': 'KS',
        })
        self.assertTrue(form.is_valid())

    def test_userprofileform_blank(self):
        form = forms.UserProfileForm({})
        self.assertTrue(form.is_valid())

    def test_invitations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/invitations/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invitations Received")
        self.assertContains(response, "Invitations Sent")
        self.assertContains(response, "rupert@oi.mate", status_code=200)

        self.invitation.expired = True
        self.invitation.save()

        response = self.client.get('/profile/invitations/')
        self.assertNotContains(response, "rupert@oi.mate", status_code=200)

    def test_image_upload(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a" * 1024
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/profile/images/', {'image': image})
        self.assertEqual(response.status_code, 200)

        images = models.UserImage.objects.filter(user=self.user.userprofile)
        self.assertEqual(len(images), 1)

        image = images[0]
        response = self.client.get('/profile/images/')
        self.assertContains(response, image.image.url, status_code=200)

        image.delete()
        images = models.UserImage.objects.filter(user=self.user.userprofile)
        self.assertEqual(len(images), 0)

    def test_image_upload_error_size(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a" * 1024 * 1024 * 5
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/profile/images/', {'image': image})
        content = response.content.decode('ascii')
        content = ast.literal_eval(content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["is_valid"], "f")
        self.assertEqual(content["redirect"], "error_size")

        images = models.UserImage.objects.filter(user=self.user.userprofile)
        self.assertEqual(len(images), 0)

    def test_image_upload_error_type(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a"
        image = SimpleUploadedFile("notimage.txt", content, content_type="text/html")
        response = self.client.post('/profile/images/', {'image': image})
        content = response.content.decode('ascii')
        content = ast.literal_eval(content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["is_valid"], "f")
        self.assertEqual(content["redirect"], "error_type")

        images = models.UserImage.objects.filter(user=self.user.userprofile)
        self.assertEqual(len(images), 0)

    def test_update_card(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/profile/card/update/', {'name': "new!", 'id': self.card.id, 'save': "save"})
        self.assertRedirects(response, '/profile/billing/', 302, 200)
        card = models.StripeCard.objects.get(id=self.card.id)
        self.assertEqual(card.name, "new!")

    def test_delete_card(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/profile/card/update/', {'id': self.card.id, 'delete': "delete"})

        self.assertRedirects(response, '/profile/billing/', 302, 200)
        cards = models.StripeCard.objects.all()
        self.assertNotIn(self.card, cards)

    def test_notification_preferences(self):
        self.assertEqual(has_notification(self.user2, 'notification_email_donation'), True)
        self.assertEqual(has_notification(self.user2, 'notification_email_campaign_created'), False)

    def test_notification_preferences_default(self):
        self.assertEqual(has_notification(self.user3, 'notification_email_donation'), True)
        self.assertEqual(has_notification(self.user3, 'notification_email_campaign_created'), True)

    def test_notification_preferences_update(self):
        self.client.login(username='testuser', password='testpassword')

        data = {'notification_preferences[]': ['notification_email_donation']}
        response = self.client.post('/profile/notifications/', data)
        self.assertRedirects(response, '/profile/notifications/', 302, 200)
        response = self.client.get('/profile/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notification Preferences")
        response = response.content.decode("utf-8")
        self.assertEqual(response.count("checked"), 1)

        data = {'notification_preferences[]': ['notification_email_donation', 'notification_email_campaign_created']}
        response = self.client.post('/profile/notifications/', data)
        self.assertRedirects(response, '/profile/notifications/', 302, 200)
        response = self.client.get('/profile/notifications/')
        response = response.content.decode("utf-8")
        self.assertEqual(response.count("checked"), 2)

    def test_taxes(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/profile/taxes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Donated ${} to {} (501c) on".format(int(self.donation.amount / 100), self.page.name))
