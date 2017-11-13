#from django.utils import timezone
from datetime import datetime

import sendgrid
from sendgrid.helpers.mail import *

from pagefund.utils import email


def error_email(error):
    user = error["user"]
    page = error["page"]
    campaign = error["campaign"]
    message = error["e"]
    date = datetime.now()

    body = "We got a Stripe error for user pk:{} on ".format(user)
    if campaign is not None:
        body =+ "campaign pk:{} ".format(campaign)
    else:
        body += "page pk:{} ".format(page)
    body += "at {}. Full message: {}".format(date, message)
    email("gn9012@gmail.com", "ERROR: Stripe", body)
