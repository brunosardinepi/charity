from collections import OrderedDict
from itertools import chain
import os
import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from django.core.mail import send_mail
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from allauth.account.signals import email_confirmed
from sendgrid.helpers.mail import *
import sendgrid
import stripe

from donation.models import Donation
from invitations.models import ManagerInvitation
from pagefund import config, settings
from pagefund.utils import email
from plans.models import StripePlan


stripe.api_key = config.settings['stripe_api_sk']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    notification_email_campaign_created = models.BooleanField(default=True)
    notification_email_donation = models.BooleanField(default=True)
    STATE_CHOICES = (
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    )
    state = models.CharField(
        max_length=100,
        choices=STATE_CHOICES,
        default='',
    )

    def __str__(self):
        return (self.user.email)

    def get_absolute_url(self):
        return reverse('userprofile:userprofile')

    def is_admin(self, obj):
        name = type(obj).__name__
        if name == "Campaign":
            return self in obj.campaign_admins.all()
        elif name == "Page":
            return self in obj.admins.all()

    def is_manager(self, obj):
        name = type(obj).__name__
        if name == "Campaign":
            return self in obj.campaign_managers.all()
        elif name == "Page":
            return self in obj.managers.all()

    def donations(self):
        return Donation.objects.filter(user=self.user).order_by('-date')

    def images(self):
        return UserImage.objects.filter(user=self)

    def invitations(self):
        return ManagerInvitation.objects.filter(invite_from=self.user, expired=False)

    def active_campaigns(self):
        admin_campaigns = self.campaign_admins.filter(deleted=False, is_active=True)
        manager_campaigns = self.campaign_managers.filter(deleted=False, is_active=True)
        subscribed_campaigns = self.campaign_subscribers.filter(deleted=False, is_active=True)
        campaigns = list(chain(admin_campaigns, manager_campaigns, subscribed_campaigns))
        campaigns = sorted(set(campaigns),key=lambda x: x.end_date)
        return campaigns

    def inactive_campaigns(self):
        admin_campaigns = self.campaign_admins.filter(deleted=False, is_active=False)
        manager_campaigns = self.campaign_managers.filter(deleted=False, is_active=False)
        subscribed_campaigns = self.campaign_subscribers.filter(deleted=False, is_active=False)
        campaigns = list(chain(admin_campaigns, manager_campaigns, subscribed_campaigns))
        campaigns = sorted(set(campaigns),key=lambda x: x.end_date)
        return campaigns

    def my_pages(self):
        admin_pages = self.page_admins.filter(deleted=False)
        manager_pages = self.page_managers.filter(deleted=False)
        subscribed_pages = self.subscribers.filter(deleted=False)
        pages = list(chain(admin_pages, manager_pages, subscribed_pages))
        pages = sorted(set(pages),key=lambda x: x.name)
        return pages

    def notification_preferences(self):
        notifications = OrderedDict()
        notifications["notification_email_campaign_created"] = {
            "value": self.notification_email_campaign_created,
            "label": "A Campaign is created for my Pages"
        }
        notifications["notification_email_donation"] = {
            "value": self.notification_email_donation,
            "label": "I make a donation"
        }
        return notifications

    def plans(self):
        return StripePlan.objects.filter(user=self.user)

    def profile_picture(self):
        try:
            return UserImage.objects.get(user=self, profile_picture=True)
        except UserImage.DoesNotExist:
            return None

    def saved_cards(self):
        return StripeCard.objects.filter(user=self.user.userprofile)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

        date = timezone.now().strftime("%Y-%m-%d %I:%M:%S %Z")
        email("gn9012@gmail.com", "blank", "blank", "admin_new_user_signup", {
            '-email-': instance.email,
            '-date-': date,
        })

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(email_confirmed, dispatch_uid="email_confirmed")
def email_confirmed_(request, email_address, **kwargs):
    email_address = str(email_address)
    email_address = email_address.split(' ')[0]
    if not settings.TESTING:
        user = User.objects.get(email=email_address)
        metadata = {'user_pk': user.pk}
        customer = stripe.Customer.create(
            email=user.email,
            metadata=metadata
        )

        user.userprofile.stripe_customer_id = customer.id
        user.save()

        data = [
          {
            'email': user.email,
            'source': 'signup',
          }
        ]
        sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
        response = sg.client.contactdb.recipients.post(request_body=data)

    email(user.email, "blank", "blank", "new_user_signup", {})

def create_random_string(length=30):
    if length <= 0:
        length = 30

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(symbols) for x in range(length)])

def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "media/user/images/%s.%s" % (create_random_string(), ext)
    return filename

class UserImage(models.Model):
    user = models.ForeignKey('userprofile.UserProfile', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    image = models.FileField(upload_to=upload_to, max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    profile_picture = models.BooleanField(default=False)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        width, height = get_image_dimensions(self.image)
        self.width = width
        self.height = height
        super(UserImage, self).save(*args, **kwargs)

@receiver(post_delete, sender=UserImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

class StripeCard(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stripe_card_id = models.CharField(max_length=255)
    stripe_card_fingerprint = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    default = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(default=timezone.now)
