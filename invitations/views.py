from django.shortcuts import render

from . import models


def pending_invitations(request):
    invitations = models.ManagerInvitation.objects.filter(invite_to=request.user.email, expired=False, accepted=False)
    return render(request, 'invitations/pending_invitations.html', {'invitations': invitations})
