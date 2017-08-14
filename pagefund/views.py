from django.db.models import Sum
from django.shortcuts import render

from allauth.account import views

from campaign.models import Campaign
from page.models import Page


def home(request):
    sponsored = Page.objects.filter(is_sponsored=True)
    page_donations = Page.objects.aggregate(Sum('donation_money'))
    campaign_donations = Campaign.objects.aggregate(Sum('donation_money'))
    donations = int(page_donations["donation_money__sum"]) + int(campaign_donations["donation_money__sum"])
    if request.user.is_authenticated:
        subscriptions = request.user.userprofile.subscribers.all()
        return render(request, 'home.html', {'subscriptions': subscriptions, 'donations': donations, 'sponsored': sponsored})
    return render(request, 'home.html', {'donations': donations, 'sponsored': sponsored})


class LoginView(views.LoginView):
    template_name = 'login.html'


class SignupView(views.SignupView):
    template_name = 'signup.html'


class PasswordResetView(views.PasswordResetView):
    template_name = 'password_reset.html'
