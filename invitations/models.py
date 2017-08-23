from django.db import models
from django.contrib.auth.models import User

import string
import random


def random_key(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ManagerInvitation(models.Model):
    expired = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    key = models.CharField(max_length=32, default=random_key)
    date_created = models.DateTimeField(auto_now_add=True)
    invite_to = models.EmailField()
    invite_from = models.OneToOneField(User, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_invite = models.BooleanField(default=False)

