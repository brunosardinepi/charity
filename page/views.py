from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import forms
from . import models
from campaign import models as CampaignModels
from invitations.models import ManagerInvitation
from pagefund.email import email
from userprofile.models import UserProfile

import json


def page(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    active_campaigns = CampaignModels.Campaign.objects.filter(page=page, is_active=True)
    inactive_campaigns = CampaignModels.Campaign.objects.filter(page=page, is_active=False)
    managers = page.managers.all()
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
        'managers': managers,
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
            email(request.user, subject, body)
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

@login_required
def page_invite(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    admin = request.user.userprofile in page.admins.all()
    print("admin = %s" % admin)
#    manager = request.user.userprofile in page.managers.all()
    # need to check if they have the invite permission
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_invite_page', page):
        manager = True
        print("manager = True")
    else:
        manager = False
        print("manager = False")
#    print("manager = %s" % manager)
    if admin or manager:
        print("True")
        form = forms.ManagerInviteForm()
        if request.method == 'POST':
            form = forms.ManagerInviteForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']

                try:
                    user = User.objects.get(email=email)
                    print("user found")
                    if user.userprofile in page.managers.all():
                        print("user is already a manager")
                        return HttpResponseRedirect(page.get_absolute_url())
                except User.DoesNotExist:
                    print("no user found")

                try:
                    invitation = ManagerInvitation.objects.get(
                        invite_to=email,
                        invite_from=request.user,
                        page=page
                    )
                except ManagerInvitation.DoesNotExist:
                    invitation = None

                if invitation:
                    print("invitation already exists")
                    return HttpResponseRedirect(page.get_absolute_url())
                else:
                    invitation = ManagerInvitation.objects.create(
                        invite_to=form.cleaned_data['email'],
                        invite_from=request.user,
                        page=page,
                        manager_edit_page=form.cleaned_data['manager_edit_page'],
                        manager_delete_page=form.cleaned_data['manager_delete_page'],
                        manager_invite_page=form.cleaned_data['manager_invite_page'],
                    )

                    msg = MIMEMultipart('alternative')
                    subject = "Page invitation!"
                    body = """
                        %s %s has invited you to become an admin of the '%s' Page.
                        <a href='http://garrett.page.fund:8000/invite/accept/%s/%s'>Click here to accept.</a>
                        """ % (
                            request.user.userprofile.first_name,
                            request.user.userprofile.last_name,
                            page.name,
                            invitation.pk,
                            invitation.key
                        )
                    body = MIMEText(body, 'html')
                    msg.attach(body)
                    print(msg)
    #                print(msg.as_string())
    #                email(user, subject, body)
                    return HttpResponseRedirect(page.get_absolute_url())
        return render(request, 'page/page_invite.html', {'form': form, 'page': page})
    else:
        return HttpResponseRedirect(page.get_absolute_url())
