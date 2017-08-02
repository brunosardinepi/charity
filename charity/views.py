from django.shortcuts import render

from allauth.account import views


def home(request):
    return render(request, 'home.html')


class LoginView(views.LoginView):
    template_name = 'login.html'


class SignupView(views.SignupView):
    template_name = 'signup.html'


class PasswordResetView(views.PasswordResetView):
    template_name = 'password_reset.html'
