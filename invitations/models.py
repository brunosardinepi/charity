from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from campaign.models import Campaign
from page.models import Page

import string
import random


def random_key(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ManagerInvitation(models.Model):
    expired = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    key = models.CharField(max_length=32, default=random_key)
    date_created = models.DateTimeField(default=timezone.now)
    invite_to = models.EmailField()
    invite_from = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.CASCADE)
    manager_edit = models.BooleanField(default=False)
    manager_delete = models.BooleanField(default=False)
    manager_invite = models.BooleanField(default=False)
    manager_upload = models.BooleanField(default=False)

class GeneralInvitation(models.Model):
    expired = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    key = models.CharField(max_length=32, default=random_key)
    date_created = models.DateTimeField(default=timezone.now)
    invite_to = models.EmailField()
    invite_from = models.ForeignKey(User, on_delete=models.CASCADE)
