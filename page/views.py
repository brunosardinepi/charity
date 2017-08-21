from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from . import forms
from . import models
from campaign import models as CampaignModels
from pagefund import config
from userprofile.models import UserProfile

import json
import smtplib


def email(user, subject, body):
    username = config.settings['email_user']
    password = config.settings['email_password']

    from_email = "noreply@page.fund"
    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_email, user.email, subject)
    msg+=body

    server = smtplib.SMTP(config.settings['email_host'], 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, [user.email], msg)
    server.quit()

def page(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    active_campaigns = CampaignModels.Campaign.objects.filter(page=page, is_active=True)
    inactive_campaigns = CampaignModels.Campaign.objects.filter(page=page, is_active=False)
    try:
        user_subscription_check = page.subscribers.get(user_id=request.user.pk)
    except UserProfile.DoesNotExist:
        user_subscription_check = None
    if user_subscription_check:
        subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
    else:
        subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}
    return render(request, 'page/page.html', {
        'page': page,
        'active_campaigns': active_campaigns,
        'inactive_campaigns': inactive_campaigns,
        'subscribe_attr': subscribe_attr
    })

@login_required
def page_create(request):
    form = forms.PageForm()
    if request.method == 'POST':
        form = forms.PageForm(request.POST)
        if form.is_valid():
            page = form.save()
            page.admins.add(request.user.userprofile)
            page.subscribers.add(request.user.userprofile)

            subject = "Page created!"
            body = "You just created a Page for: %s" % page.name
            page_email(request.user, subject, body)
            return HttpResponseRedirect(page.get_absolute_url())
    return render(request, 'page/page_create.html', {'form': form})

@login_required
def page_edit(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    if request.user.userprofile in page.admins.all():
        form = forms.PageForm(instance=page)
        if request.method == 'POST':
            form = forms.PageForm(instance=page, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'page/page_edit.html', {'page': page, 'form': form})

@login_required
def page_delete(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    if request.user.userprofile in page.admins.all():
        form = forms.DeletePageForm(instance=page)
        if request.method == 'POST':
            form = forms.DeletePageForm(request.POST, instance=page)
            page.delete()
            return HttpResponseRedirect(reverse('home'))
    else:
        raise Http404
    return render(request, 'page/page_delete.html', {'form': form, 'page': page})

@login_required
def subscribe(request, page_pk, action=None):
    page = get_object_or_404(models.Page, pk=page_pk)
    if action == "subscribe":
        page.subscribers.add(request.user.userprofile)
        new_subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
    elif action == "unsubscribe":
        page.subscribers.remove(request.user.userprofile)
        new_subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}
    else:
        print("something went wrong")
    new_subscribe_attr = json.dumps(new_subscribe_attr)
    return HttpResponse(new_subscribe_attr)
