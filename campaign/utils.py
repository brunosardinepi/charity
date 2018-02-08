import urllib.request as urllib

from django.db.models import Sum

import sendgrid
from sendgrid.helpers.mail import Email, Content, Substitution, Mail

from donation.models import Donation
from pagefund import config, settings


def campaign_duration(campaign):
    if campaign.end_date is not None:
        duration = campaign.end_date - campaign.created_on
        return duration.days

def campaign_reached_goal(campaign):
    if campaign.is_active is False:
        donations = Donation.objects.filter(campaign=campaign).aggregate(Sum('amount')).get('amount__sum')
        if donations is not None and donations >= campaign.goal:
            return True
        else:
            return False
