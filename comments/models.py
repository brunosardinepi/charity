from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=3000)
    date = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "{}: {}".format(self.user, self.comment[:50])
