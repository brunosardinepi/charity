import datetime
from itertools import chain

from django.core.management.base import BaseCommand
from django.utils import timezone

from invitations import models


class Command(BaseCommand):
    help = 'Sets expired flag for invitations'

    def handle(self, *args, **options):
        expire_date = timezone.now() - datetime.timedelta(days=3)
        password_expire_date = timezone.now() - datetime.timedelta(days=1)

        manager_invitations = models.ManagerInvitation.objects.filter(date_created__lte=expire_date, expired=False, accepted=False, declined=False)
        general_invitations = models.GeneralInvitation.objects.filter(date_created__lte=expire_date, expired=False, accepted=False, declined=False)
        forgot_password_requests = models.ForgotPasswordRequest.objects.filter(date_created__lte=password_expire_date, expired=False, completed=False)

        invitations = list(chain(manager_invitations, general_invitations, forgot_password_requests))

        for i in invitations:
            i.expired = True
            i.save()
