import urllib.request as urllib

import sendgrid
from sendgrid.helpers.mail import Email, Content, Substitution, Mail

from pagefund import config


def email_new_campaign(email_to):
    sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
    from_email = Email("no-reply@page.fund")
    subject = "I'm replacing the subject tag"
    to_email = Email(email_to)
    content = Content("text/html", "I'm replacing the <strong>body tag</strong>")
    mail = Mail(from_email, subject, to_email, content)
    mail.personalizations[0].add_substitution(Substitution("-name-", "Example User"))
    mail.personalizations[0].add_substitution(Substitution("-city-", "Denver"))
    mail.template_id = "0f0ff154-4a0e-48eb-b073-d59447ac67e8"
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except urllib.HTTPError as e:
        print (e.read())
        exit()
    print(response.status_code)
    print(response.body)
    print(response.headers)
