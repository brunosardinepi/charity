from django.core.management.base import BaseCommand

import stripe

from page.models import Page


class Command(BaseCommand):
    help = 'Checks all Pages for their Stripe verification status'

    def handle(self, *args, **options):
        pages = Page.objects.all()
        for page in pages:
            account = stripe.Account.retrieve(page.stripe_account_id)
            print(account['legal_entity']['verification']['status'])
            status = account['legal_entity']['verification']['status']
            if status == 'verified':
                page.stripe_verified = True
            else:
                page.stripe_verified = False
            page.save()