import random
import os
import string
from collections import OrderedDict

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.images import get_image_dimensions
from django.db import models
from django.db.models.signals import post_delete
from django.db.models import Sum
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from comments.models import Comment
from donation.models import Donation
from pagefund import config


class Campaign(models.Model):
    campaign_admins = models.ManyToManyField('userprofile.UserProfile', related_name='campaign_admins', blank=True)
    campaign_managers = models.ManyToManyField('userprofile.UserProfile', related_name='campaign_managers', blank=True)
    campaign_slug = models.SlugField(max_length=255)
    campaign_subscribers = models.ManyToManyField('userprofile.UserProfile', related_name='campaign_subscribers', blank=True)
    comments = GenericRelation(Comment)
    created_on = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    deleted_on = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    end_date = models.DateTimeField()
    goal = models.IntegerField()
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255, db_index=True)
    page = models.ForeignKey('page.Page', on_delete=models.CASCADE, related_name='campaigns')
    trending_score = models.DecimalField(default=0, max_digits=10, decimal_places=1)
    event_location = models.TextField(blank=True)
    website = models.CharField(max_length=128, blank=True)

    CATEGORY_CHOICES = (
        ('animal', 'Animal'),
        ('environment', 'Environment'),
        ('education', 'Education'),
        ('other', 'Other'),
        ('religious', 'Religious'),
    )
    category = models.CharField(
        max_length=255,
        choices=CATEGORY_CHOICES,
        default='other',
    )

    TYPE_CHOICES = (
#        ('event', 'Event'),
        ('general', 'General'),
        ('vote', 'Vote'),
    )
    type = models.CharField(
        max_length=255,
        choices=TYPE_CHOICES,
        default='general',
    )

    class Meta:
        permissions = (
            ('manager_edit', 'Manager -- edit Campaign'),
            ('manager_delete', 'Manager -- delete Campaign'),
            ('manager_invite', 'Manager -- invite users to manage Campaign'),
            ('manager_image_edit', 'Manager -- upload media to Campaign'),
            ('manager_view_dashboard', 'Manager -- view Campaign dashboard'),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('campaign', kwargs={
            'page_slug': self.page.page_slug,
            'campaign_pk': self.pk,
            'campaign_slug': self.campaign_slug
            })

    def save(self, *args, **kwargs):
        # if this campaign is new
        if not self.pk:
            # create a new campaign_slug
            self.campaign_slug = slugify(self.name)

        self.category = self.page.category
        super(Campaign, self).save(*args, **kwargs)

    def get_model(self):
        return self.__class__.__name__

    def top_donors(self):
        donors = Donation.objects.filter(campaign=self).values_list('user', flat=True).distinct()
        top_donors = {}
        for d in donors:
            if d is not None:
                user = get_object_or_404(User, pk=d)
                total_amount = Donation.objects.filter(user=user, campaign=self, anonymous_amount=False, anonymous_donor=False).aggregate(Sum('amount')).get('amount__sum')
                if total_amount is not None:
                    top_donors[d] = {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'amount': total_amount
                    }
                    if user.userprofile.profile_picture():
                        top_donors[d]['image_url'] = user.userprofile.profile_picture().image.url
                        top_donors[d]['image_pk'] = user.userprofile.profile_picture().pk
        top_donors = OrderedDict(sorted(top_donors.items(), key=lambda t: t[1]['amount'], reverse=True))
        top_donors = list(top_donors.items())[:10]
        return top_donors

    def images(self):
        return CampaignImage.objects.filter(campaign=self)

    def profile_picture(self):
        try:
            return CampaignImage.objects.get(campaign=self, profile_picture=True)
        except CampaignImage.MultipleObjectsReturned:
            # multiple profile images returned
            return None
        except CampaignImage.DoesNotExist:
            return None

    def donations(self):
        return Donation.objects.filter(campaign=self).order_by('-date')

    def donations_recent(self):
        return Donation.objects.filter(campaign=self).order_by('-date')[:10]

    def donation_count(self):
        return Donation.objects.filter(campaign=self).count()

    def donation_money(self):
        d = Donation.objects.filter(campaign=self).aggregate(Sum('amount')).get('amount__sum')
        if d is None:
            return 0
        else:
            return d

    def managers_list(self):
        return self.campaign_managers.all()

    def vote_participants(self):
        p = list(VoteParticipant.objects.filter(campaign=self))
        random.shuffle(p)
        p.sort(key= lambda t: t.vote_amount(), reverse=True)
        return p

    def unique_donors(self):
        return Donation.objects.filter(campaign=self).distinct('donor_first_name').distinct('donor_last_name').count()

    def search_description(self):
        if len(self.description) > 300:
            return self.description[:300] + "..."
        else:
            return self.description

def create_random_string(length=30):
    if length <= 0:
        length = 30

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(symbols) for x in range(length)])

def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "media/images/%s.%s" % (create_random_string(), ext)
    return filename

class VoteParticipant(models.Model):
    name = models.CharField(max_length=255)
    campaign = models.ForeignKey('campaign.Campaign', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to, blank=True)

    def __str__(self):
        return self.name

    def vote_amount(self):
        d = Donation.objects.filter(campaign=self.campaign, campaign_participant=self).aggregate(Sum('amount')).get('amount__sum')
        if d is None:
            return 0
        else:
            return d

class CampaignImage(models.Model):
    campaign = models.ForeignKey('campaign.Campaign', on_delete=models.CASCADE)
    image = models.FileField(upload_to=upload_to, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    profile_picture = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        width, height = get_image_dimensions(self.image)
        self.width = width
        self.height = height
        super(CampaignImage, self).save(*args, **kwargs)

@receiver(post_delete, sender=CampaignImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
