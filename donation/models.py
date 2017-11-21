from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Donation(models.Model):
    amount = models.IntegerField()
    anonymous_amount = models.BooleanField(default=False)
    anonymous_donor = models.BooleanField(default=False)
    campaign = models.ForeignKey('campaign.Campaign', on_delete=models.CASCADE, blank=True, null=True)
    campaign_participant = models.ForeignKey('campaign.VoteParticipant', on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    page = models.ForeignKey('page.Page', on_delete=models.CASCADE, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    donor_first_name = models.CharField(max_length=255, blank=True, null=True)
    donor_last_name = models.CharField(max_length=255, blank=True, null=True)

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

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.user:
                self.donor_first_name = self.user.first_name
                self.donor_last_name = self.user.last_name
        super(Donation, self).save(*args, **kwargs)
