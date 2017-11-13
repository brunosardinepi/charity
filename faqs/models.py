from django.db import models
from django.utils import timezone


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    downvotes = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=1)
