from allauth.account import views
from allauth.socialaccount import views as social_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.views import View

from . import config
from . import forms
from .utils import email
from campaign.models import Campaign
from donation.models import Donation
from invitations.models import GeneralInvitation
from page.models import Page


def home(request):
    donations = Donation.objects.all().aggregate(Sum('amount')).get('amount__sum')
    return render(request, 'home.html', {'donations': donations})

class LoginView(views.LoginView):
    template_name = 'login.html'

class SignupView(views.SignupView):
    template_name = 'signup.html'

class SocialSignupView(social_views.SignupView):
    template_name = 'social_signup.html'

class EmailVerificationSentView(views.EmailVerificationSentView):
    template_name = 'verification_sent.html'

@login_required
def invite(request):
    form = forms.GeneralInviteForm()
    if request.method == 'POST':
        form = forms.GeneralInviteForm(request.POST)
        if form.is_valid():
            # check if the person we are inviting is already on PageFund
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                if user.userprofile:
                    return redirect('notes:error_invite_user_exists')
            except User.DoesNotExist:
                pass

            # check if the user has already been invited by this person
            # expired should be False, otherwise the previous invitation has expired and we are OK with them getting a new one
            # accepted/declined are irrelevant if the invite has expired, so we don't check these
            try:
                invitation = GeneralInvitation.objects.get(
                    invite_to=form.cleaned_data['email'],
                    invite_from=request.user,
                    expired=False
                )
            except GeneralInvitation.DoesNotExist:
                invitation = None

            # if this user has already been invited, redirect the person inviting them
            # need to notify them that the person has already been invited
            if invitation:
                # this user has already been invited, so do nothing
                return HttpResponseRedirect(reverse('home'))
            # if the user hasn't been invited already, create the invite and send it to them
            else:
                # create the invitation object and set the permissions
                invitation = GeneralInvitation.objects.create(
                    invite_to=form.cleaned_data['email'],
                    invite_from=request.user,
                )

                # create the email
                substitutions = {
                    "-signupurl-": "{}/invite/accept/{}/{}/".format(config.settings['site'], invitation.pk, invitation.key),
                }
                email(form.cleaned_data['email'], "blank", "blank", "pagefund_invitation", substitutions)

                return HttpResponseRedirect(reverse('home'))
    return render(request, 'invite.html', {'form': form})

def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
