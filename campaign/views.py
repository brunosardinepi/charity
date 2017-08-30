from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.core.exceptions import ValidationError
from . import forms
from . import models
from page.models import Page
from pagefund.email import email


def campaign(request, page_slug, campaign_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    return render(request, 'campaign/campaign.html', {'page': page, 'campaign': campaign})

@login_required
def campaign_create(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    form = forms.CampaignForm()
    if request.method == 'POST':
        form = forms.CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('campaign_icon',FALSE)
            image_type = image.content_type.split('/')[0]
            if image_type in settings.UPLOAD_TYPES:
                if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                        msg = 'The file size limit is %s. Your file size is %s.' % (
                            settings.MAX_IMAGE_UPLOAD_SIZE,
                            image._size
                        )
                        raise ValidationError(msg)
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.page = page
            campaign.save()

            subject = "Campaign created!"
            body = "A Campaign called '%s' has just been created by %s for the '%s' Page." % (
                campaign.name,
                request.user.email,
                page.name
            )
            email(request.user, subject, body)
            # once the page admins have been re-structured, need to email them when a campaign is created for their page
            return HttpResponseRedirect(campaign.get_absolute_url())
    return render(request, 'campaign/campaign_create.html', {'form': form, 'page': page})

@login_required
def campaign_edit(request, page_slug, campaign_slug):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    if request.user == campaign.user:
        form = forms.CampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.CampaignForm(instance=campaign, data=request.POST, files=request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('campaign_icon',False)
                image_type = image.content_type.split('/')[0]
                if image_type in settings.UPLOAD_TYPES:
                    if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                        msg = 'The file size limit is %s. Your file size is %s.' % (
                            settings.MAX_IMAGE_UPLOAD_SIZE,
                            image._size
                        )
                        raise ValidationError(msg)

                form.save()
                return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_edit.html', {'campaign': campaign, 'form': form})

@login_required
def campaign_delete(request, page_slug, campaign_slug):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    if request.user == campaign.user:
        form = forms.DeleteCampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.DeleteCampaignForm(request.POST, instance=campaign)
            campaign.delete()
            return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_delete.html', {'form': form, 'campaign': campaign})
