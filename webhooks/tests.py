from django.test import Client, TestCase

from .models import Webhook


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
