import urllib.request as urllib

from django.db.models import Sum

import sendgrid
from sendgrid.helpers.mail import Email, Content, Substitution, Mail

from donation.models import Donation
from pagefund import config, settings


def email_new_campaign(email_to, campaign):
    if not settings.TESTING:
        sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
        from_email = Email(config.settings["email_from"])
        subject = "null"
        to_email = Email(email_to)
        content = Content("text/html", "null")
        mail = Mail(from_email, subject, to_email, content)
        mail.personalizations[0].add_substitution(Substitution("-campaign-", campaign.name))
        mail.personalizations[0].add_substitution(Substitution("-page-", campaign.page.name))
        mail.template_id = "0f0ff154-4a0e-48eb-b073-d59447ac67e8"
        try:
            response = sg.client.mail.send.post(request_body=mail.get())
        except urllib.HTTPError as e:
            exit()

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
