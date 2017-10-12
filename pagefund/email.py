import sendgrid
from sendgrid.helpers.mail import *

from . import config


def email(user_email, subject, body):
    sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
    from_email = Email("no-reply@page.fund")
    to_email = Email(user_email)
    subject = subject
    content = Content("text/plain", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
