from django.db import models
from django.contrib.auth.models import User

from campaign.models import Campaign
from page.models import Page


class CommentTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True)
    upvotes = models.IntegerField(default=1)
    downvotes = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class Comment(CommentTemplate):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, blank=True, null=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.page:
            return "Page;%s;%s;%s" % (self.page.name, self.user, self.date)
        elif self.campaign:
            return "Campaign;%s;%s;%s" % (self.campaign.name, self.user, self.date)

    def get_absolute_url(self):
        if self.page:
            return reverse('page', kwargs={'page_slug': self.page.page_slug})
        elif self.campaign:
            return reverse('campaign', kwargs={
                'page_slug': self.campaign.page.page_slug,
                'campaign_pk': self.campaign.pk,
                'campaign_slug': self.campaign.campaign_slug
            })

class Reply(CommentTemplate):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "replies"
