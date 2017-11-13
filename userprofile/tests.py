import ast

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase

from . import forms
from . import models
from . import views
from donation.models import Donation
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
            first_name='John',
            last_name='Doe',
        )
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

        self.campaign2 = Campaign.objects.create(
            name='Mousepad',
            page=self.page2,
            type='Event',
            description='I use a mousepad.',
            goal='15',
            donation_count='1',
            donation_money='2'
        )

        self.campaign2.campaign_managers.add(self.user.userprofile)

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
            user=self.user
        )

        self.donation2 = Donation.objects.create(
            amount=900,
            page=self.page,
            campaign=self.campaign,
            user=self.user
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
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, '$%s to <a href="/%s/">%s</a> @' % (
            int(self.donation.amount / 100),
            self.page.page_slug,
            self.page.name),
            status_code=200
        )
        self.assertContains(response, '$%s to <a href="/%s/">%s</a> via <a href="/%s/%s/%s/">%s</a> @' % (
            int(self.donation2.amount / 100),
            self.page.page_slug,
            self.page.name,
            self.page.page_slug,
            self.campaign.pk,
            self.campaign.campaign_slug,
            self.campaign.name),
            status_code=200
        )

    def test_userprofileform(self):
        form = forms.UserProfileForm({
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': '1990-09-23',
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
        content = b"a" * 1024
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/profile/images/', {'image': image})
        self.assertEqual(response.status_code, 200)

        images = models.UserImage.objects.filter(user=self.user.userprofile)
        self.assertEqual(len(images), 1)

        image = images[0]
        response = self.client.get('/profile/')
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
        self.assertRedirects(response, '/profile/', 302, 200)
        card = models.StripeCard.objects.get(id=self.card.id)
        self.assertEqual(card.name, "new!")

    def test_delete_card(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/profile/card/update/', {'id': self.card.id, 'delete': "delete"})

        self.assertRedirects(response, '/profile/', 302, 200)
        cards = models.StripeCard.objects.all()
        self.assertNotIn(self.card, cards)

    def test_notification_preferences(self):
        self.client.login(username='testuser', password='testpassword')

        data = {'notification_preferences[]': ['notification_email_page_donation']}
        response = self.client.post('/profile/notifications/update/', data)
        self.assertRedirects(response, '/profile/', 302, 200)
        response = self.client.get('/profile/')
        response = response.content.decode("utf-8")
        self.assertEqual(response.count("checked"), 1)

        data = {'notification_preferences[]': ['notification_email_page_donation', 'notification_email_page_created']}
        response = self.client.post('/profile/notifications/update/', data)
        self.assertRedirects(response, '/profile/', 302, 200)
        response = self.client.get('/profile/')
        response = response.content.decode("utf-8")
        self.assertEqual(response.count("checked"), 2)
