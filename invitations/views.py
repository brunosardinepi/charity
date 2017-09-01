from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from guardian.shortcuts import assign_perm

from . import models


def remove_invitation(invitation_pk, accepted, declined):
    invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
    invitation.expired = "True"
    invitation.accepted = accepted
    invitation.declined = declined
    invitation.save()

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
    if (int(invitation_pk) == int(invitation.pk)) and (key == invitation.key) and (request.user.email == invitation.invite_to):
        permissions = {
            'manager_edit': invitation.manager_edit,
            'manager_delete': invitation.manager_delete,
            'manager_invite': invitation.manager_invite,
        }
        if invitation.page:
            invitation.page.managers.add(request.user.userprofile)
            for k, v in permissions.items():
                if v == True:
                    assign_perm(k, request.user, invitation.page)
            remove_invitation(invitation_pk, "True", "False")
            return HttpResponseRedirect(invitation.page.get_absolute_url())
        elif invitation.campaign:
            invitation.campaign.campaign_managers.add(request.user.userprofile)
            for k, v in permissions.items():
                if v == True:
                    assign_perm(k, request.user, invitation.campaign)
            remove_invitation(invitation_pk, "True", "False")
            return HttpResponseRedirect(invitation.campaign.get_absolute_url())
    else:
        print("bad")

def decline_invitation(request, invitation_pk, key):
    invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
    if (int(invitation_pk) == int(invitation.pk)) and (key == invitation.key):
        remove_invitation(invitation_pk, "False", "True")
    else:
        print("bad")

    # if the user is logged in and declined the invitation, redirect them to their other pending invitations
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('invitations:pending_invitations'))
    # if the user isn't logged in and declined the invitation, redirect them to the homepage
    else:
        return HttpResponseRedirect(reverse('home'))
