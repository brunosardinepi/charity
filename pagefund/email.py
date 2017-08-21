from . import config

import smtplib


def email(user, subject, body):
    username = config.settings['email_user']
    password = config.settings['email_password']

    from_email = "noreply@page.fund"
    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_email, user.email, subject)
    msg+=body

    server = smtplib.SMTP(config.settings['email_host'], 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, [user.email], msg)
    server.quit()
