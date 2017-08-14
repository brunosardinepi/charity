from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from . import forms
from . import models
from page.models import Page


def campaign(request, page_slug, campaign_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    return render(request, 'campaign/campaign.html', {'page': page, 'campaign': campaign})

@login_required
def campaign_delete(request, page_slug, campaign_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    if request.user.userprofile in page.admins.all():
        form = forms.DeleteCampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.DeleteCampaignForm(request.POST, instance=campaign)
            campaign.delete()
            return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_delete.html', {'form': form, 'campaign': campaign})
