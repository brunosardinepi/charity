from django.shortcuts import get_object_or_404, render

from . import models


def campaign(request, page_slug, campaign_slug):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    return render(request, 'campaign/campaign.html', {'campaign': campaign})

