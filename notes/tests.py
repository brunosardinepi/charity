from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .forms import AbuseCommentForm
from .models import Note
from campaign.models import Campaign
from comments.models import Comment
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

        self.comment = Comment.objects.create(
            user=self.user,
            comment="This is a comment.",
            content_type=ContentType.objects.get_for_model(self.page),
            object_id=self.page.pk,
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

    def test_note_form(self):
        data = {}
        form = AbuseCommentForm(data)
        self.assertFalse(form.is_valid())

        data = {'note': "A test note for you."}
        form = AbuseCommentForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form['note'], "A test note for you.")

    def test_comments_abuse(self):
        # notes/abuse/comment/16/
        self.client.login(username='testuser', password='testpassword')
        self.assertEqual(Note.objects.all().count(), 2)
        data = {'note': "How rude!"}
        response = self.client.post('/notes/abuse/comment/{}/'.format(self.comment.pk), data)

        self.assertRedirects(response, '/', 302, 200)
        self.assertEqual(Note.objects.all().count(), 3)
