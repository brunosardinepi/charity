from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from . import models


@login_required
def pending_invitations(request):
    invitations = models.ManagerInvitation.objects.filter(
        invite_to=request.user.email,
        expired=False,
        accepted=False
    )
    return render(request, 'invitations/pending_invitations.html', {'invitations': invitations})

@login_required
def accept_invitation(request, invitation_pk, key):
    invitation = get_object_or_404(models.ManagerInvitation, pk=invitation_pk)
    print(invitation.pk)
    print(invitation.key)
    return HttpResponseRedirect(invitation.page.get_absolute_url())
