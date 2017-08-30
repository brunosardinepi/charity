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

@login_required
def accept_invitation(request, invitation_pk, key):
    invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
    if (int(invitation_pk) == int(invitation.pk)) and (key == invitation.key) and (request.user.email == invitation.invite_to):
        invitation.page.managers.add(request.user.userprofile)
        permissions = {
            'manager_edit_page': invitation.manager_edit_page,
            'manager_delete_page': invitation.manager_delete_page,
            'manager_invite_page': invitation.manager_invite_page,
        }
        for k, v in permissions.items():
            if v == True:
                assign_perm(k, request.user, invitation.page)
        remove_invitation(invitation_pk, "True", "False")
    else:
        print("bad")
    return HttpResponseRedirect(invitation.page.get_absolute_url())

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
