from django.db.models import Sum
from django.shortcuts import render

from allauth.account import views

from campaign.models import Campaign
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


class PasswordResetView(views.PasswordResetView):
    template_name = 'password_reset.html'
