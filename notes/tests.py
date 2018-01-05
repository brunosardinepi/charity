from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .forms import AbuseCommentForm
from .models import Note
from campaign.models import Campaign
from comments.models import Comment, Reply
from page.models import Page

import unittest


class NoteTest(TestCase):
    def setUp(self):
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
            category='Animal'
        )

        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            campaign_slug='testcampaign',
            page=self.page,
            description='This is a description for Test Campaign.',
            goal='11',
        )

        self.comment = Comment.objects.create(
            user=self.user,
            content="This is a comment.",
            page=self.page
        )

        self.comment2 = Comment.objects.create(
            user=self.user,
            content="This is another comment.",
            campaign=self.campaign
        )

        self.reply = Reply.objects.create(
            user=self.user2,
            content="This is a reply.",
            comment=self.comment
        )

        self.reply2 = Reply.objects.create(
            user=self.user3,
            content="This is another reply.",
            comment=self.comment2
        )

        self.note = Note.objects.create(
            details="these are test details for this note",
            message="i don't like this comment",
            user=self.user,
            type="abuse",
        )

        self.note2 = Note.objects.create(
            details="some details for this other note",
            message="this is a bad reply",
            user=self.user2,
            type="abuse",
        )

    def test_note_exists(self):
        notes = Note.objects.all()

        self.assertIn(self.note, notes)
        self.assertIn(self.note2, notes)

    def test_notes_creation_time(self):
        note = Note.objects.create(
            user=self.user,
            details="somebody submitted this",
            message="hello there",
        )
        now = timezone.now()
        self.assertLess(note.date, now)

    def test_note_comment(self):
        response = self.client.get('/notes/abuse/comment/comment/{}/'.format(
            self.comment.pk))
        self.assertRedirects(response,
            '/accounts/login/?next=/notes/abuse/comment/comment/{}/'.format(
                self.comment.pk), 302, 200)

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/notes/abuse/comment/comment/{}/'.format(
            self.comment.pk))
        self.assertEquals(response.status_code, 200)

        data = {'note': "This is my note."}
        response = self.client.post('/notes/abuse/comment/comment/{}/'.format(
            self.comment.pk), data)
        self.assertRedirects(response, '/', 302, 200)

    def test_note_form(self):
        data = {}
        form = AbuseCommentForm(data)
        self.assertFalse(form.is_valid())

        data = {'note': "A test note for you."}
        form = AbuseCommentForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form['note'], "A test note for you.")
