from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from . import forms
from campaign.models import Campaign
from page.models import Page


def comment_page(request, page_pk):
    page = get_object_or_404(Page, pk=page_pk)
    form = forms.CommentForm()
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.page = page
            comment.save()
            return HttpResponseRedirect(page.get_absolute_url())
        else:
            return Http404

def comment_campaign(request, campaign_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    form = forms.CommentForm()
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.campaign = campaign
            comment.save()
            return HttpResponseRedirect(campaign.get_absolute_url())
        else:
            return Http404

