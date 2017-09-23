from allauth.account import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse

from . import config
from . import forms
from .email import email
from campaign.models import Campaign
from invitations.models import GeneralInvitation
from page.models import Page


def home(request):
    sponsored = Page.objects.filter(is_sponsored=True, deleted=False)
    page_donations = Page.objects.filter(deleted=False).aggregate(Sum('donation_money'))
    if page_donations["donation_money__sum"] == None:
        page_donations = 0
    else:
        page_donations = int(page_donations["donation_money__sum"])
    campaign_donations = Campaign.objects.filter(deleted=False).aggregate(Sum('donation_money'))
    if campaign_donations["donation_money__sum"] == None:
        campaign_donations = 0
    else:
        campaign_donations = int(campaign_donations["donation_money__sum"])
    donations = page_donations + campaign_donations
    if request.user.is_authenticated:
        subscriptions = request.user.userprofile.subscribers.filter(deleted=False)
        return render(request, 'home.html', {'subscriptions': subscriptions, 'donations': donations, 'sponsored': sponsored})
    return render(request, 'home.html', {'donations': donations, 'sponsored': sponsored})


class LoginView(views.LoginView):
    template_name = 'login.html'


class SignupView(views.SignupView):
    template_name = 'signup.html'


#class PasswordResetView(views.PasswordResetView):
#    template_name = 'password_reset.html'

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
                    return redirect('error:error_invite_user_exists')
            except User.DoesNotExist:
                print("no user found, good!")

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
                subject = "PageFund invitation!"
                body = "%s %s has invited you to join PageFund! <a href='%s/invite/accept/%s/%s/'>Click here to accept.</a> <a href='%s/invite/general/decline/%s/%s/'>Click here to decline.</a>" % (
                    request.user.userprofile.first_name,
                    request.user.userprofile.last_name,
                    config.settings['site'],
                    invitation.pk,
                    invitation.key,
                    config.settings['site'],
                    invitation.pk,
                    invitation.key
                )
                email(form.cleaned_data['email'], subject, body)
                # redirect the inviting person
                return HttpResponseRedirect(reverse('home'))
    return render(request, 'invite.html', {'form': form})
