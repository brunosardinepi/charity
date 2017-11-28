from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse
from guardian.shortcuts import assign_perm

from . import forms
from . import models
from .utils import invitation_is_good, remove_invitation
from pagefund import config
from pagefund.utils import email


@login_required
def pending_invitations(request):
    invitations = models.ManagerInvitation.objects.filter(
        invite_to=request.user.email,
        expired=False,
        accepted=False,
        declined=False
    )
    return render(request, 'invitations/pending_invitations.html', {'invitations': invitations})

@login_required(login_url='signup')
def accept_invitation(request, invitation_pk, key):
    invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
    if invitation_is_good(request, invitation, key) == True:
        permissions = {
            'manager_edit': invitation.manager_edit,
            'manager_delete': invitation.manager_delete,
            'manager_invite': invitation.manager_invite,
            'manager_image_edit': invitation.manager_image_edit,
            'manager_view_dashboard': invitation.manager_view_dashboard
        }
        if invitation.page:
            invitation.page.managers.add(request.user.userprofile)
            invitation.page.subscribers.add(request.user.userprofile)
            for k, v in permissions.items():
                if v == True:
                    assign_perm(k, request.user, invitation.page)
            remove_invitation(invitation_pk, "manager", "True", "False")
            return HttpResponseRedirect(invitation.page.get_absolute_url())
        elif invitation.campaign:
            invitation.campaign.campaign_managers.add(request.user.userprofile)
            invitation.campaign.campaign_subscribers.add(request.user.userprofile)
            for k, v in permissions.items():
                if v == True:
                    assign_perm(k, request.user, invitation.campaign)
            remove_invitation(invitation_pk, "manager", "True", "False")
            return HttpResponseRedirect(invitation.campaign.get_absolute_url())
    else:
        print("bad")

@login_required(login_url='signup')
def accept_general_invitation(request, invitation_pk, key):
    invitation = get_object_or_404(models.GeneralInvitation, pk=invitation_pk)
    if invitation_is_good(request, invitation, key) == True:
        remove_invitation(invitation_pk, "general", "True", "False")
        return HttpResponseRedirect(reverse('home'))
    else:
        print("bad")

def decline_invitation(request, type, invitation_pk, key):
    if type == 'manager':
        invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
    elif type == 'general':
        invitation = get_object_or_404(models.GeneralInvitation, pk=invitation_pk)
    if (int(invitation_pk) == int(invitation.pk)) and (key == invitation.key):
        remove_invitation(invitation_pk, type, "False", "True")
    else:
        print("bad")

    # if the user is logged in and declined the invitation, redirect them to their other pending invitations
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('invitations:pending_invitations'))
    # if the user isn't logged in and declined the invitation, redirect them to the homepage
    else:
        return HttpResponseRedirect(reverse('home'))

def forgot_password_request(request):
    form = forms.ForgotPasswordRequestForm()
    if request.method == "POST":
        form = forms.ForgotPasswordRequestForm(request.POST)
        if form.is_valid():
            invitation = models.ForgotPasswordRequest.objects.create(email=form.cleaned_data['email'])
            subject = "Forgot password"
            body = "You submitted a request to reset your password. <a href='%s/password/reset/%s/%s/'>Click here to reset your password.</a>" % (
                config.settings['site'],
                invitation.pk,
                invitation.key
            )
            email(form.cleaned_data['email'], subject, body)
            return HttpResponseRedirect(reverse('home'))
    return render(request, 'forgot_password_request.html', {'form': form})

def forgot_password_reset(request, invitation_pk, key):
    form = forms.ForgotPasswordResetForm()
    if request.method == "POST":
        form = forms.ForgotPasswordResetForm(request.POST)
        if form.is_valid():
            invitation = get_object_or_404(models.ForgotPasswordRequest, pk=invitation_pk)
            if invitation.expired == True:
                return redirect('error:error_forgotpasswordreset_expired')
            elif invitation.completed == True:
                return redirect('error:error_forgotpasswordreset_completed')
            else:
                if (int(invitation_pk) == int(invitation.pk)) and (key == invitation.key):
                    invitation.expired = True
                    invitation.completed = True
                    invitation.save()

                    user = get_object_or_404(User, email=invitation.email)
                    user.set_password(form.cleaned_data['password1'])
                    user.save()
                    return HttpResponseRedirect(reverse('home'))
    return render(request, 'forgot_password_reset.html', {'form': form})
