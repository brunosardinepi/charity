from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import config

import smtplib


def email(user_email, subject, body):
    username = config.settings['email_user']
    password = config.settings['email_password']

    from_email = "noreply@page.fund"
    msg = MIMEMultipart('alternative')
#    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_email, user.email, subject)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = user_email

    html = body
    part1 = MIMEText(html, 'html')

    msg.attach(part1)

    server = smtplib.SMTP(config.settings['email_host'], 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
#    server.sendmail(from_email, [user.email], msg)
    server.sendmail(from_email, [user_email], msg.as_string())
    server.quit()
