from django.db import models
from django.utils import timezone


class Webhook(models.Model):
    event_id = models.CharField(max_length=255)
    object = models.CharField(max_length=255)
    created = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    event = models.TextField()
