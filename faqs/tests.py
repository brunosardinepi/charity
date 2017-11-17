import unittest

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from . import models
from . import views
from faqs.models import FAQ
from votes.models import Vote


class FAQTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
            first_name = 'John',
            last_name = 'Doe',
        )

        self.user2 = User.objects.create_user(
            username='harrypotter',
            email='harry@potter.com',
            password='imawizard',
            first_name = 'Lord',
            last_name = 'Voldemort',
        )

        self.faq = FAQ.objects.create(
            question="This is a FAQ question.",
            answer="And here's the answer.",
        )

        self.faq2 = FAQ.objects.create(
            question="How can she slap?",
            answer="Instain mother.",
        )

        self.vote = Vote.objects.create(
            user=self.user,
            score=1,
            faq=self.faq,
        )

        self.vote2 = Vote.objects.create(
            user=self.user,
            score=-1,
            faq=self.faq2,
        )

        self.vote3 = Vote.objects.create(
            user=self.user2,
            score=1,
            faq=self.faq,
        )

        self.vote4 = Vote.objects.create(
            user=self.user2,
            score=1,
            faq=self.faq2,
        )

    def test_faq_exists(self):
        faqs = FAQ.objects.all()

        self.assertIn(self.faq, faqs)
        self.assertIn(self.faq2, faqs)

    def test_faq_creation_time(self):
        faq = FAQ.objects.create(question="Q?", answer="A!")
        now = timezone.now()
        self.assertLess(faq.date, now)

    def test_faq_page(self):
        response = self.client.get('/faq/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.faq.question)
        self.assertContains(response, self.faq.answer)
        self.assertContains(response, '<button id="upvotes-f-{}" class="vote upvote'.format(self.faq.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq.upvotes()))
        self.assertContains(response, '<button id="downvotes-f-{}" class="vote downvote'.format(self.faq.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq.downvotes()))
        self.assertContains(response, self.faq2.question)
        self.assertContains(response, self.faq2.answer)
        self.assertContains(response, '<button id="upvotes-f-{}" class="vote upvote'.format(self.faq2.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq2.upvotes()))
        self.assertContains(response, '<button id="downvotes-f-{}" class="vote downvote'.format(self.faq2.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq2.downvotes()))

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/faq/')
        self.assertContains(response, self.faq.question)
        self.assertContains(response, self.faq.answer)
        self.assertContains(response, '<button id="upvotes-f-{}" class="vote upvote'.format(self.faq.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq.upvotes()))
        self.assertContains(response, '<button id="downvotes-f-{}" class="vote downvote'.format(self.faq.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq.downvotes()))
        self.assertContains(response, self.faq2.question)
        self.assertContains(response, self.faq2.answer)
        self.assertContains(response, '<button id="upvotes-f-{}" class="vote upvote'.format(self.faq2.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq2.upvotes()))
        self.assertContains(response, '<button id="downvotes-f-{}" class="vote downvote'.format(self.faq2.pk))
        self.assertContains(response, '">{}</button>'.format(self.faq2.downvotes()))
