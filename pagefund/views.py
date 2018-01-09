from allauth.account import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.views import View

from . import config
from . import forms
from .utils import email
from campaign.models import Campaign
from django_comments.models import Comment
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
                    return redirect('notes:error_invite_user_exists')
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
                    request.user.first_name,
                    request.user.last_name,
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


class CommentPosted(View):
    def get(self, request):
        c = request.GET.get('c')
        if c:
            comment = Comment.objects.get(pk=c)
            if comment:
                obj = comment.content_object
                if obj.get_model() == "Page":
                    return HttpResponseRedirect("/{}/#c{}".format(obj.page_slug, comment.pk))
                elif obj.get_model() == "Campaign":
                    return HttpResponseRedirect("/{}/{}/{}/#c{}".format(
                        obj.page.page_slug,
                        obj.pk,
                        obj.campaign_slug,
                        comment.pk,
                    ))
