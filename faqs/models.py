from django.db import models
from django.utils import timezone


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.question[:10]
