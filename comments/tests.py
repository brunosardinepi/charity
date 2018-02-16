import datetime
import pytz

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm

from . import models
from . import views
from campaign.models import Campaign
from page.models import Page

import unittest


class CommentTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
            first_name = 'John',
            last_name = 'Doe'
        )

        self.user2 = User.objects.create_user(
            username='harrypotter',
            email='harry@potter.com',
            password='imawizard',
            first_name = 'Lord',
            last_name = 'Voldemort'
        )

        self.user3 = User.objects.create_user(
            username='bobdole',
            email='bob@dole.com',
            password='dogsarecool'
        )

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
            description='This is a description for Test Page.',
            category='Animal',
            stripe_verified=True,
        )

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='testcampaign',
            page=self.page,
            description='This is a description for Test Campaign.',
            goal='11',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.comment = models.Comment.objects.create(
            user=self.user,
            comment="This is a comment.",
            content_type=ContentType.objects.get_for_model(self.page),
            object_id=self.page.pk,
        )

    def test_comment_exists(self):
        comments = models.Comment.objects.all()

        self.assertIn(self.comment, comments)

    def test_comment_creation_time(self):
        comment = models.Comment.objects.create(
            user=self.user,
            comment="hello mars",
            content_type=ContentType.objects.get_for_model(self.page),
            object_id=self.page.pk,
        )
        now = timezone.now()
        self.assertLess(comment.date, now)

    def test_comment_page(self):
        data = {'comment': "I am anonymous!"}
        response = self.client.post('/comments/post/{}/{}/'.format(ContentType.objects.get_for_model(self.page).pk, self.page.pk), data)
        self.assertRedirects(response, '/accounts/login/?next=/comments/post/{}/{}/'.format(ContentType.objects.get_for_model(self.page).pk, self.page.pk), 302, 200)

        response = self.client.get('/{}/'.format(self.page.page_slug))
        self.assertNotContains(response, "I am anonymous!", status_code=200)

        self.client.login(username='testuser', password='testpassword')
        self.assertEqual(models.Comment.objects.all().count(), 1)
        data = {'comment': "Hello my name is Testy McTestface."}
        response = self.client.post('/comments/post/{}/{}/'.format(ContentType.objects.get_for_model(self.page).pk, self.page.pk), data)

        comment = models.Comment.objects.get(comment="Hello my name is Testy McTestface.")
        self.assertRedirects(response, '/{}/#c{}'.format(self.page.page_slug, comment.pk), 302, 200)
        self.assertEqual(models.Comment.objects.all().count(), 2)

        response = self.client.get('/{}/'.format(self.page.page_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello my name is Testy McTestface.")
        self.assertContains(response, "{} {}".format(self.user.first_name, self.user.last_name))

    def test_comment_page_loggedout(self):
        response = self.client.get('/{}/'.format(self.page.page_slug))
        self.assertContains(response, 'You must be logged in to comment.')

    def test_comment_page_loggedin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/'.format(self.page.page_slug))
        self.assertNotContains(response, 'You must be logged in to comment.')

