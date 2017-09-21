from django.contrib.auth.models import AnonymousUser, User
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
            password='testpassword'
        )
        self.user.userprofile.first_name = 'John'
        self.user.userprofile.last_name = 'Doe'
        self.user.save()

        self.user2 = User.objects.create_user(
            username='harrypotter',
            email='harry@potter.com',
            password='imawizard'
        )
        self.user2.userprofile.first_name = 'Lord'
        self.user2.userprofile.last_name = 'Voldemort'
        self.user2.save()

        self.user3 = User.objects.create_user(
            username='bobdole',
            email='bob@dole.com',
            password='dogsarecool'
        )

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='testcampaign',
            page=self.page,
            description='This is a description for Test Campaign.',
            goal='11',
            donation_count='21',
            donation_money='31'
        )

        self.comment = models.Comment.objects.create(
            user=self.user,
            content="This is a comment.",
            page=self.page
        )

        self.comment2 = models.Comment.objects.create(
            user=self.user,
            content="This is another comment.",
            campaign=self.campaign
        )

        self.reply = models.Reply.objects.create(
            user=self.user2,
            content="This is a reply.",
            comment=self.comment
        )

        self.reply2 = models.Reply.objects.create(
            user=self.user3,
            content="This is another reply.",
            comment=self.comment2
        )

    def test_comment_exists(self):
        comments = models.Comment.objects.all()

        self.assertIn(self.comment, comments)
        self.assertIn(self.comment2, comments)

    def test_comment_creation_time(self):
        comment = models.Comment.objects.create(user=self.user, content="hello mars", page=self.page)
        now = timezone.now()
        self.assertLess(comment.date, now)

    def test_reply_exists(self):
        replies = models.Reply.objects.all()

        self.assertIn(self.reply, replies)
        self.assertIn(self.reply2, replies)

    def test_reply_creation_time(self):
        reply = models.Reply.objects.create(user=self.user, content="hello mars", comment=self.comment)
        now = timezone.now()
        self.assertLess(reply.date, now)

    def test_comment_page(self):
        data = {'comment_text': "I am anonymous!"}
        response = self.client.post('/comments/page/%s/comment/' % self.page.pk, data)
        self.assertRedirects(response, '/accounts/login/?next=/comments/page/%s/comment/' % self.page.pk, 302, 200)
        response = self.client.get('/testpage/')
        self.assertNotContains(response, "I am anonymous!", status_code=200)
        self.assertContains(response, "You must be logged in to comment!", status_code=200)

        self.client.login(username='testuser', password='testpassword')
        self.assertEqual(models.Comment.objects.all().count(), 2)
        data = {'comment_text': "Hello my name is Testy McTestface."}
        response = self.client.post('/comments/page/%s/comment/' % self.page.pk, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Comment.objects.all().count(), 3)

        response = self.client.get('/testpage/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello my name is Testy McTestface.", status_code=200)
        self.assertContains(response, "%s %s" % (self.user.userprofile.first_name, self.user.userprofile.last_name), status_code=200)

        comment = models.Comment.objects.get(content="Hello my name is Testy McTestface.")
        response = self.client.get('/comments/delete/comment/%s/' % comment.pk)
        response = self.client.get('/testpage/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, comment.content, status_code=200)

    def test_comment_campaign(self):
        data = {'comment_text': "Oi mate!"}
        response = self.client.post('/comments/campaign/%s/comment/' % self.campaign.pk, data)
        self.assertRedirects(response, '/accounts/login/?next=/comments/campaign/%s/comment/' % self.campaign.pk, 302, 200)
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertNotContains(response, "Oi mate!", status_code=200)
        self.assertContains(response, "You must be logged in to comment!", status_code=200)

        self.client.login(username='testuser', password='testpassword')
        self.assertEqual(models.Comment.objects.all().count(), 2)
        data = {'comment_text': "First night in town."}
        response = self.client.post('/comments/campaign/%s/comment/' % self.campaign.pk, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Comment.objects.all().count(), 3)

        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First night in town.", status_code=200)
        self.assertContains(response, "%s %s" % (self.user.userprofile.first_name, self.user.userprofile.last_name), status_code=200)

        comment = models.Comment.objects.get(content="First night in town.")
        response = self.client.get('/comments/delete/comment/%s/' % comment.pk)
        response = self.client.get('/%s/%s/%s/' % (self.page.page_slug, self.campaign.pk, self.campaign.campaign_slug))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, comment.content, status_code=200)

    def test_reply(self):
        self.client.login(username='testuser', password='testpassword')
        data = {'reply_text': "This is my reply."}
        response = self.client.post('/comments/%s/reply/' % self.comment.pk, data)
        response = self.client.get('/testpage/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is my reply.", status_code=200)
        self.assertContains(response, "%s %s" % (self.user.userprofile.first_name, self.user.userprofile.last_name), status_code=200)

        self.client.login(username='harrypotter', password='imawizard')
        data = {'reply_text': "Yankee Doodle went to town."}
        response = self.client.post('/comments/%s/reply/' % self.comment.pk, data)
        response = self.client.get('/testpage/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Yankee Doodle went to town.", status_code=200)
        self.assertContains(response, "%s %s" % (self.user2.userprofile.first_name, self.user2.userprofile.last_name), status_code=200)

        self.assertContains(response, self.reply.content, status_code=200)
        response = self.client.get('/comments/delete/reply/%s/' % self.reply.pk)
        response = self.client.get('/testpage/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.reply.content, status_code=200)

        self.client.login(username='testuser', password='testpassword')
        replies = models.Reply.objects.filter(comment=self.comment)
        response = self.client.get('/comments/delete/comment/%s/' % self.comment.pk)
        response = self.client.get('/testpage/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.comment.content, status_code=200)
        for r in replies:
            self.assertNotContains(response, r.content, status_code=200)

    def test_delete_comment_not_owner(self):
        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/comments/delete/comment/%s/' % self.comment.pk)
        self.assertEqual(response.status_code, 404)

    def test_delete_reply_not_owner(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/comments/delete/reply/%s/' % self.reply.pk)
        self.assertEqual(response.status_code, 404)
