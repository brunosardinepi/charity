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

def create_error(error, request):
    err = Note.objects.create(
        date = timezone.now(),
        message = str(error),
        user = request.user,
        type = 'error',
    )

    substitutions = {
        '-pk-': str(err.pk),
        '-user-': err.user.email,
        '-message-': err.message,
    }
    email("gn9012@gmail.com", "blank", "blank", "note_error", substitutions)

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
    email("abuse@page.fund", subject, body, "note_abuse", {})
