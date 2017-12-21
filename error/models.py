from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Error(models.Model):
    date = models.DateTimeField(default=timezone.now)
    details = models.TextField()
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
