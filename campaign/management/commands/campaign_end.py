from django.core.management.base import BaseCommand
from django.utils import timezone

from campaign.models import Campaign


class Command(BaseCommand):
    help = 'Closes the campaigns that are set to end'

    def handle(self, *args, **options):
        campaigns = Campaign.objects.filter(end_date__lte=timezone.now(), is_active=True)
        for c in campaigns:
            c.is_active = False
            c.save()
