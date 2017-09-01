from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from guardian.shortcuts import assign_perm, get_user_perms, remove_perm

from . import forms
from . import models
from invitations.models import ManagerInvitation
from page.models import Page
from pagefund.email import email


def campaign(request, page_slug, campaign_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    managers = campaign.campaign_managers.all()

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
            user_permissions = get_user_perms(user, campaign)
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
    return render(request, 'campaign/campaign.html', {'page': page, 'campaign': campaign, 'managers': managers})

@login_required
def campaign_create(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    form = forms.CampaignForm()
    if request.method == 'POST':
        form = forms.CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.page = page
            campaign.save()
            campaign.campaign_admins.add(request.user.userprofile)

            subject = "Campaign created!"
            body = "A Campaign called '%s' has just been created by %s for the '%s' Page." % (
                campaign.name,
                request.user.email,
                page.name
            )
            email(request.user, subject, body)

            admins = page.admins.all()
            for admin in admins:
                email(admin.user, subject, body)
            managers = page.managers.all()
            for manager in managers:
                email(manager.user, subject, body)

            return HttpResponseRedirect(campaign.get_absolute_url())
    return render(request, 'campaign/campaign_create.html', {'form': form, 'page': page})

@login_required
def campaign_edit(request, page_slug, campaign_slug):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    admin = request.user.userprofile in campaign.campaign_admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_edit', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
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
    admin = request.user.userprofile in campaign.campaign_admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_delete', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
        form = forms.DeleteCampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.DeleteCampaignForm(request.POST, instance=campaign)
            campaign.delete()
            return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_delete.html', {'form': form, 'campaign': campaign})

@login_required
def campaign_invite(request, page_slug, campaign_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, page=page, campaign_slug=campaign_slug)
    # True if the user is an admin
    admin = request.user.userprofile in campaign.campaign_admins.all()
    # True if the user is a manager and has the 'invite' permission
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_invite', campaign):
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
                    if user.userprofile in campaign.campaign_managers.all():
                        return HttpResponseRedirect(campaign.get_absolute_url())
                except User.DoesNotExist:
                    print("no user found")

                # check if the user has already been invited by this admin/manager for this campaign
                # expired should be False, otherwise the previous invitation has expired and we are OK with them getting a new one
                # accepted/declined are irrelevant if the invite has expired, so we don't check these
                try:
                    invitation = ManagerInvitation.objects.get(
                        invite_to=user_email,
                        invite_from=request.user,
                        campaign=campaign,
                        expired=False
                    )
                except ManagerInvitation.DoesNotExist:
                    invitation = None

                # if this user has already been invited, redirect the admin/manager
                # need to notify the admin/manager that the person has already been invited
                if invitation:
                    print("this user has already been invited, so do nothing")
                    return HttpResponseRedirect(campaign.get_absolute_url())
                # if the user hasn't been invited already, create the invite and send it to them
                else:
                    # create the invitation object and set the permissions
                    invitation = ManagerInvitation.objects.create(
                        invite_to=form.cleaned_data['email'],
                        invite_from=request.user,
                        campaign=campaign,
                        manager_edit=form.cleaned_data['manager_edit'],
                        manager_delete=form.cleaned_data['manager_delete'],
                        manager_invite=form.cleaned_data['manager_invite'],
                    )

                    # create the email
                    subject = "Campaign invitation!"
                    body = "%s %s has invited you to become an admin of the '%s' campaign. <a href='http://garrett.page.fund:8000/invite/accept/%s/%s/'>Click here to accept.</a> <a href='http://garrett.page.fund:8000/invite/decline/%s/%s/'>Click here to decline.</a>" % (
                            request.user.userprofile.first_name,
                            request.user.userprofile.last_name,
                            campaign.name,
                            invitation.pk,
                            invitation.key,
                            invitation.pk,
                            invitation.key
                        )
                    email(user, subject, body)
                    # redirect the admin/manager to the campaign
                    return HttpResponseRedirect(campaign.get_absolute_url())
        return render(request, 'campaign/campaign_invite.html', {'form': form, 'campaign': campaign})
    # the user isn't an admin or a manager, so they can't invite someone
    # the only way someone got here was by typing the url manually
    else:
        raise Http404

@login_required
def remove_manager(request, campaign_slug, manager_pk):
    campaign = get_object_or_404(models.Campaign, campaign_slug=campaign_slug)
    manager = get_object_or_404(User, pk=manager_pk)
    # only campaign admins can remove managers
    if request.user.userprofile in campaign.campaign_admins.all():
        # remove the manager
        campaign.campaign_managers.remove(manager.userprofile)
        # revoke the permissions
        remove_perm('manager_edit', manager, campaign)
        remove_perm('manager_delete', manager, campaign)
        remove_perm('manager_invite', manager, campaign)
        # redirect to campaign
        return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404
