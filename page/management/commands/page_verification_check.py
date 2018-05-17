from django.core.management.base import BaseCommand

import stripe

from page.models import Page
from pagefund.utils import email, has_notification


class Command(BaseCommand):
    help = 'Checks all Pages for their Stripe verification status'

    def handle(self, *args, **options):
        pages = Page.objects.filter(deleted=False)
        for page in pages:
            account = stripe.Account.retrieve(page.stripe_account_id)
            status = account['legal_entity']['verification']['status']
            if status == 'verified' or status == 'pending':
                page.stripe_verified = True
            else:
                page.stripe_verified = False

                # email the admins
                admins = page.admins.all()
                for admin in admins:
                    if has_notification(admin.user, "notification_email_campaign_created") == True:
                        substitutions = {
                            "-pagename-": page.name,
                            "-pageslug-": page.page_slug,
                        }
                        email(admin.user.email, "blank", "blank", "page_verification", substitutions)

            page.save()