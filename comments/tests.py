from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
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

        self.user4 = User.objects.create_user(
            username='batman',
            email='batman@bat.cave',
            password='imbatman'
        )

        self.user5 = User.objects.create_user(
            username='newguy',
            email='its@me.com',
            password='imnewhere'
        )

        self.page = Page.objects.create(
            name='Test Page',
            page_slug='testpage',
            description='This is a description for Test Page.',
            donation_count='20',
            donation_money='30',
            category='Animal'
        )

        self.page.admins.add(self.user.userprofile)
        self.page.managers.add(self.user3.userprofile)
        assign_perm('manager_edit', self.user3, self.page)
        assign_perm('manager_delete', self.user3, self.page)
        assign_perm('manager_invite', self.user3, self.page)

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            page=self.page,
            description='This is a description for Test Campaign.',
            goal='11',
            donation_count='21',
            donation_money='31'
        )

        self.campaign2 = Campaign.objects.create(
            name='Another One',
            page=self.page,
            description='My cat died yesterday',
            goal='12',
            donation_count='22',
            donation_money='33'
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

    def test_comment_exists(self):
        replies = models.Reply.objects.all()

        self.assertIn(self.reply, replies)
        self.assertIn(self.reply2, replies)
