from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm

from . import models
from . import views
from campaign.models import Campaign
from page.models import Page


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

        now = timezone.now()
        self.assertLess(self.comment.date, now)

    def test_reply_exists(self):
        replies = models.Reply.objects.all()

        self.assertIn(self.reply, replies)
        self.assertIn(self.reply2, replies)

    def test_comment_page(self):
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
