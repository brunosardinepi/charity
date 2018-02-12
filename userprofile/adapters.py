import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from allauth.account.adapter import DefaultAccountAdapter

from pagefund import utils


class CustomAccountAdapter(DefaultAccountAdapter):

    def clean_password(self, password, user=None):
        if re.match(r'^(?=.*\d).{7,}$', password):
            return password
        else:
            raise ValidationError("Your password must be at least 7 characters and contain at least 1 number.")

    def send_mail(self, template_prefix, email, context):
        template = template_prefix.split('/')[2]

        user = context['user']
        user = User.objects.get(username=user)

        # email the user
        substitutions = {
            "-key-": context['key'],
        }
        utils.email(user.email, "blank", "blank", template, substitutions)
