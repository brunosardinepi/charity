from django import forms


class ForgotPasswordRequestForm(forms.Form):
    email = forms.EmailField()
