from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from . import forms
from . import models
from .utils import comment_attributes
from campaign.models import Campaign
from page.models import Page

import json


@login_required
def comment(request, model, pk):
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if model == "page":
            page = get_object_or_404(Page, pk=pk)
            comment = models.Comment.objects.create(
                user=request.user,
                content=comment_text,
                page=page
            )
        elif model == "campaign":
            campaign = get_object_or_404(Campaign, pk=pk)
            comment = models.Comment.objects.create(
                user=request.user,
                content=comment_text,
                campaign=campaign
            )
        response_data = comment_attributes(comment)
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

@login_required
def reply(request, comment_pk):
    comment = get_object_or_404(models.Comment, pk=comment_pk)
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text')

        reply = models.Reply.objects.create(
            user=request.user,
            content=reply_text,
            comment=comment
        )
        response_data = comment_attributes(reply)
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

@login_required
def delete(request, model, pk):
    if model == "comment":
        obj = get_object_or_404(models.Comment, pk=pk)
        replies = models.Reply.objects.filter(comment_id=obj.pk)
        if replies:
            for r in replies:
                r.deleted = True
                r.deleted_on = timezone.now()
                r.save()
    elif model == "reply":
        obj = get_object_or_404(models.Reply, pk=pk)
    if obj.user == request.user:
        obj.deleted = True
        obj.deleted_on = timezone.now()
        obj.save()
        return HttpResponse('')
    else:
        raise Http404
