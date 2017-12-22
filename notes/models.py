from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Note(models.Model):
    date = models.DateTimeField(default=timezone.now)
    details = models.TextField()
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    TYPE_CHOICES = (
        ('feedback', 'Feedback'),
        ('abuse', 'Abuse'),
        ('error', 'Error'),
        ('contact', 'Contact'),
    )
    type = models.CharField(
        max_length=255,
        choices=TYPE_CHOICES,
        default='',
    )

