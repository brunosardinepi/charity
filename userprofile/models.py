import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from allauth.account.signals import user_signed_up
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
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    notification_email_pagefund_news = models.BooleanField(default=True)
    notification_email_page_created = models.BooleanField(default=True)
    notification_email_campaign_created = models.BooleanField(default=True)
    notification_email_page_manager = models.BooleanField(default=True)
    notification_email_campaign_manager = models.BooleanField(default=True)
    notification_email_page_donation = models.BooleanField(default=True)
    notification_email_recurring_donation = models.BooleanField(default=True)
    notification_email_campaign_donation = models.BooleanField(default=True)
    notification_email_campaign_voted = models.BooleanField(default=True)
    notification_email_campaign_ticket_purchased = models.BooleanField(default=True)
    notification_email_campaign_goal_reached = models.BooleanField(default=True)
    notification_email_campaign_ticket_sold_out = models.BooleanField(default=True)
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
        return ("%s %s" % (self.user.first_name, self.user.last_name))

    def get_absolute_url(self):
        return reverse('userprofile:userprofile')

    def admin_campaigns(self):
        return self.campaign_admins.filter(deleted=False)

    def admin_pages(self):
        return self.page_admins.filter(deleted=False)

    def donations(self):
        return Donation.objects.filter(user=self.user)

    def images(self):
        return UserImage.objects.filter(user=self)

    def invitations(self):
        return ManagerInvitation.objects.filter(invite_from=self.user, expired=False)

    def manager_campaigns(self):
        return self.campaign_managers.filter(deleted=False)

    def manager_pages(self):
        return self.page_managers.filter(deleted=False)

    def notification_preferences(self):
        notifications = {
            "notification_email_pagefund_news": self.notification_email_pagefund_news,
            "notification_email_page_created": self.notification_email_page_created,
            "notification_email_campaign_created": self.notification_email_campaign_created,
            "notification_email_page_manager": self.notification_email_page_manager,
            "notification_email_campaign_manager": self.notification_email_campaign_manager,
            "notification_email_page_donation": self.notification_email_page_donation,
            "notification_email_recurring_donation": self.notification_email_recurring_donation,
            "notification_email_campaign_donation": self.notification_email_campaign_donation,
            "notification_email_campaign_voted": self.notification_email_campaign_voted,
            "notification_email_campaign_ticket_purchased": self.notification_email_campaign_ticket_purchased,
            "notification_email_campaign_goal_reached": self.notification_email_campaign_goal_reached,
            "notification_email_campaign_ticket_sold_out": self.notification_email_campaign_ticket_sold_out
        }
        return notifications

    def plans(self):
        return StripePlan.objects.filter(user=self.user)

    def profile_picture(self):
        return UserImage.objects.get(user=self, profile_picture=True)

    def saved_cards(self):
        return StripeCard.objects.filter(user=self.user.userprofile)

    def subscriptions(self):
        return self.subscribers.filter(deleted=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(user_signed_up, dispatch_uid="user_signed_up")
def user_signed_up_(request, user, **kwargs):
    if not settings.TESTING:
        metadata = {'user_pk': user.pk}
        customer = stripe.Customer.create(
            email=user.email,
            metadata=metadata
        )

        user.userprofile.stripe_customer_id = customer.id
        user.save()

    subject = "Welcome to PageFund!"
    body = "This is a test email for a user that has just signed up with PageFund."
    email(user.email, subject, body)

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
    image = models.FileField(upload_to=upload_to, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    profile_picture = models.BooleanField(default=False)


class StripeCard(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stripe_card_id = models.CharField(max_length=255)
    stripe_card_fingerprint = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    default = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(default=timezone.now)
