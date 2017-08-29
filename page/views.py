from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from guardian.shortcuts import assign_perm, get_user_perms, remove_perm

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

    if request.method == "POST":
        post_data = request.POST.getlist('permissions[]')
        new_permissions = dict()
        for p in post_data:
            m = p.split("_", 1)[0]
            p = p.split("_", 1)[1]
            if m not in new_permissions:
                new_permissions[m] = []
            new_permissions[m].append(p)

        # get list of user's current perms
        old_permissions = dict()
        for k in new_permissions:
            user = get_object_or_404(User, pk=k)
            user_permissions = get_user_perms(user, page)
            if k not in old_permissions:
                old_permissions[k] = []
            for p in user_permissions:
                old_permissions[k].append(p)

        # for every item in the user's current perms, compare to the new list of perms from the form
        for k, v in old_permissions.items():
            user = get_object_or_404(User, pk=k)
            for e in v:
                # if that item is in the list, remove it from the new list and do nothing to the perm
                if e in new_permissions[k]:
                    new_permissions[k].remove(e)
                # if that item is not in the list, remove the perm
                else:
                    remove_perm(e, user, page)
        # for every item in the new list, give the user the perms for that item
        for k,v in new_permissions.items():
            user = get_object_or_404(User, pk=k)
            for e in v:
                assign_perm(e, user, page)
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
    admin = request.user.userprofile in page.admins.all()
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_edit_page', page):
        manager = True
    else:
        manager = False
    if admin or manager:
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
    admin = request.user.userprofile in page.admins.all()
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_delete_page', page):
        manager = True
    else:
        manager = False
    if admin or manager:
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
    # True if the user is an admin
    admin = request.user.userprofile in page.admins.all()
    # True if the user is a manager and has the 'invite' permission
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_invite_page', page):
        manager = True
    else:
        manager = False
    # if the user is either an admin or a manager, so either must be True
    if admin or manager:
        form = forms.ManagerInviteForm()
        if request.method == 'POST':
            form = forms.ManagerInviteForm(request.POST)
            if form.is_valid():
                user_email = form.cleaned_data['email']

                # check if the person we are inviting is already a manager
                try:
                    user = User.objects.get(email=user_email)
                    if user.userprofile in page.managers.all():
                        return HttpResponseRedirect(page.get_absolute_url())
                except User.DoesNotExist:
                    print("no user found")

                # check if the user has already been invited by this admin/manager for this page
                # expired should be False, otherwise the previous invitation has expired and we are OK with them getting a new one
                # accepted/declined are irrelevant if the invite has expired, so we don't check these
                try:
                    invitation = ManagerInvitation.objects.get(
                        invite_to=user_email,
                        invite_from=request.user,
                        page=page,
                        expired=False
                    )
                except ManagerInvitation.DoesNotExist:
                    invitation = None

                # if this user has already been invited, redirect the admin/manager
                # need to notify the admin/manager that the person has already been invited
                if invitation:
                    return HttpResponseRedirect(page.get_absolute_url())
                # if the user hasn't been invited already, create the invite and send it to them
                else:
                    # create the invitation object and set the permissions
                    invitation = ManagerInvitation.objects.create(
                        invite_to=form.cleaned_data['email'],
                        invite_from=request.user,
                        page=page,
                        manager_edit_page=form.cleaned_data['manager_edit_page'],
                        manager_delete_page=form.cleaned_data['manager_delete_page'],
                        manager_invite_page=form.cleaned_data['manager_invite_page'],
                    )

                    # create the email
                    subject = "Page invitation!"
                    body = "%s %s has invited you to become an admin of the '%s' Page. <a href='http://garrett.page.fund:8000/invite/accept/%s/%s/'>Click here to accept.</a> <a href='http://garrett.page.fund:8000/invite/decline/%s/%s/'>Click here to decline.</a>" % (
                            request.user.userprofile.first_name,
                            request.user.userprofile.last_name,
                            page.name,
                            invitation.pk,
                            invitation.key,
                            invitation.pk,
                            invitation.key
                        )
                    email(user, subject, body)
                    # redirect the admin/manager to the Page
                    return HttpResponseRedirect(page.get_absolute_url())
        return render(request, 'page/page_invite.html', {'form': form, 'page': page})
    # the user isn't an admin or a manager, so they can't invite someone
    # the only way someone got here was by typing the url manually
    else:
        raise Http404

@login_required
def remove_manager(request, page_slug, manager_pk):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    manager = get_object_or_404(User, pk=manager_pk)
    # only page admins can remove managers
    if request.user.userprofile in page.admins.all():
        # remove the manager
        page.managers.remove(manager.userprofile)
        # revoke the permissions
        remove_perm('manager_edit_page', manager, page)
        remove_perm('manager_delete_page', manager, page)
        remove_perm('manager_invite_page', manager, page)
        # redirect to page
        return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
