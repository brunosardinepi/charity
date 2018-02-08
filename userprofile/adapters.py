import re

from django.core.exceptions import ValidationError

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def clean_password(self, password, user=None):
        if re.match(r'^(?=.*\d).{7,}$', password):
            return password
        else:
            raise ValidationError("Your password must be at least 7 characters and contain at least 1 number.")