from django.utils import timezone

import sendgrid
from sendgrid.helpers.mail import *

from .models import Note
from page.models import Page
from pagefund.utils import email


def error_email(error):
    user = error["user"]
    page = error["page"]
    campaign = error["campaign"]
    message = error["e"]
    date = timezone.now()

    body = "We got a Stripe error for user pk:{} on page pk:{} ".format(user, page)
    if campaign is not None:
        body += "campaign pk:{} ".format(campaign)
    body += "at {}. Full message: {}".format(date, message)
    email("gn9012@gmail.com", "ERROR: Stripe", body)

def create_error(error, request, object):
    details = ""
    if isinstance(object, Page):
        details += "\naddress_line1 = {};".format(object.address_line1)
        details += "\naddress_line2 = {};".format(object.address_line2)
        details += "\ncity = {};".format(object.city)
        details += "\ndescription = {};".format(object.description)
        details += "\nein = {};".format(object.ein)
        details += "\nname = {};".format(object.name)
        details += "\npage_slug = {};".format(object.page_slug)
        details += "\ntos_accepted = {};".format(object.tos_accepted)
        details += "\nwebsite = {};".format(object.website)
        details += "\nzipcode = {};".format(object.zipcode)
        details += "\ncategory = {};".format(object.category)
        details += "\nstate = {};".format(object.state)
        details += "\ntype = {};".format(object.type)

    err = Note.objects.create(
        date = timezone.now(),
        details = details,
        message = str(error),
        user = request.user,
        type = 'error',
    )

    subject = "PageFund ERROR"
    body = "Error {} occured at {} for user {}. Message: {}; Details: {}".format(
        err.pk,
        err.date,
        err.user.email,
        err.message,
        err.details
    )
    email("gn9012@gmail.com", subject, body)

    return err

def create_note(request, obj, type):
    details = ""
    fields = [f.name for f in obj._meta.get_fields()]
    for field in fields:
        details += "{}: {};\n".format(field, getattr(obj, field))

    note = Note.objects.create(
        date = timezone.now(),
        details = details,
        message = request.POST.get('note'),
        user = request.user,
        type = type,
    )

    subject = "[{}] PageFund note".format(type.upper())
    body = "Note {} from user {} at {}; Message: {}; Details: {}".format(
        note.pk,
        note.user.email,
        note.date,
        note.message,
        note.details
    )
    email("abuse@page.fund", subject, body, None)
