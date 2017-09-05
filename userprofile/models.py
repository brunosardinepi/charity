from allauth.account.signals import user_signed_up
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from pagefund import config
from pagefund.email import email

import smtplib


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=5, blank=True)
    avatar = models.ImageField(upload_to="media/", blank=True, null=True)
    class Meta:
        ordering = ('first_name', 'last_name',)

    def __str__(self):
        return ("%s %s" % (self.first_name, self.last_name))

    def get_absolute_url(self):
        return reverse('userprofile:userprofile')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(user_signed_up, dispatch_uid="user_signed_up")
def user_signed_up_(request, user, **kwargs):
    subject = "Welcome to PageFund!"
    body = "This is a test email for a user that has just signed up with PageFund."
    email(user, subject, body)
