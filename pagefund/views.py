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

class ConfirmEmailView(views.ConfirmEmailView):
    template_name = 'email_confirm.html'

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

            # create the email
            email(form.cleaned_data['email'], "blank", "blank", "pagefund_invitation", {})

            return HttpResponseRedirect(reverse('home'))
    return render(request, 'invite.html', {'form': form})

def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
