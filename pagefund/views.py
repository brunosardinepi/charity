from django.shortcuts import render

from allauth.account import views


def home(request):
    if request.user.is_authenticated:
        subscriptions = request.user.userprofile.subscribers.all()
        return render(request, 'home.html', {'subscriptions': subscriptions})
    else:
        return render(request, 'home.html')


class LoginView(views.LoginView):
    template_name = 'login.html'


class SignupView(views.SignupView):
    template_name = 'signup.html'


class PasswordResetView(views.PasswordResetView):
    template_name = 'password_reset.html'
