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
def campaign_create(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    form = forms.CampaignForm()
    if request.method == 'POST':
        form = forms.CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.creator = request.user
            campaign.page = page
            campaign.save()
            return HttpResponseRedirect(campaign.get_absolute_url())
    return render(request, 'campaign/campaign_create.html', {'form': form, 'page': page})

@login_required
def campaign_edit(request, page_slug, campaign_slug):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    if request.user == campaign.creator:
        form = forms.CampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.CampaignForm(instance=campaign, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_edit.html', {'campaign': campaign, 'form': form})

@login_required
def campaign_delete(request, page_slug, campaign_slug):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    if request.user == campaign.creator:
        form = forms.DeleteCampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.DeleteCampaignForm(request.POST, instance=campaign)
            campaign.delete()
            return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_delete.html', {'form': form, 'campaign': campaign})
