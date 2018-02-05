from django.test import Client, TestCase

import stripe

from .models import Webhook
from pagefund import config


class WebhookTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.webhook = Webhook.objects.create(
            event_id="evt_1BqieBAlNJDWHQVy6IVfX20U",
            object="event",
            created="1517493759",
            type="balance.available",
            event="a whole bunch of dict",
        )

    def test_webhook_exists(self):
        webhooks = Webhook.objects.all()
        self.assertIn(self.webhook, webhooks)

    def test_webhooks(self):
        stripe.api_key = config.settings['stripe_api_sk']
        coupon = stripe.Coupon.retrieve('1')
        coupon.metadata['test'] = 'test'
        coupon.save()
