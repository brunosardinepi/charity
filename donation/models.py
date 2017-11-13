from django.contrib.auth.models import User
#from django.db.models.signals import post_save
from django.db import models
#from django.dispatch import receiver
from django.utils import timezone


class Donation(models.Model):
    amount = models.IntegerField()
    anonymous_amount = models.BooleanField(default=False)
    anonymous_donor = models.BooleanField(default=False)
    campaign = models.ForeignKey('campaign.Campaign', on_delete=models.CASCADE, blank=True, null=True)
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

#    @receiver(post_save, sender=User)
#    def assign_donor_name(sender, instance, created, **kwargs):
#        if created:
#            print(instance)
#            if instance.user:
#                instance.donor_first_name = instance.user.first_name
#                instance.donor_last_name = instance.user.last_name
#                instance.save()
