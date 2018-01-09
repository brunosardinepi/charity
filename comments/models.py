from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=3000)
    date = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return "{}: {}".format(self.user, self.content[:50])
