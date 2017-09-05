from django.db import models
from django.contrib.auth.models import User

from campaign.models import Campaign
from page.models import Page


class CommentTemplate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True)
    upvotes = models.IntegerField(default=1)
    downvotes = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class Comment(CommentTemplate):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, blank=True)

class Reply(CommentTemplate):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
