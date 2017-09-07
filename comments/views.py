from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime

from . import forms
from . import models
from campaign.models import Campaign
from page.models import Page

import json


def comment_page(request, page_pk):
    page = get_object_or_404(Page, pk=page_pk)
#    form = forms.CommentForm()
    if request.method == 'POST':
#        form = forms.CommentForm(request.POST)
#        if form.is_valid():
#            comment = form.save(commit=False)
#            comment.user = request.user
#            comment.page = page
#            comment.save()
#            return HttpResponseRedirect(page.get_absolute_url())
#        else:
#            return Http404
        comment_text = request.POST.get('comment_text')
        response_data = {}

        comment = models.Comment.objects.create(
            user=request.user,
            content=comment_text,
            page=page
        )

        response_data['result'] = "success"
#        response_data['comments'] = serializers.serialize(
#            'json',
#            models.Comment.objects.filter(page=page).order_by('-date')
#        )
#        response_data['comment'] = serializers.serialize('json', comment)
        response_data['content'] = comment.content
        response_data['user'] = "%s %s" % (comment.user.userprofile.first_name, comment.user.userprofile.last_name)
#        response_data['date'] = comment.date.isoformat()
        response_data['date'] = localtime(comment.date)
#        response_data['date'] = comment.date.strftime('%m/%d/%y %-I:%M %p')
        response_data['date'] = response_data['date'].strftime('%m/%d/%y %-I:%M %p')
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

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
