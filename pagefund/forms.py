from django import forms


class GeneralInviteForm(forms.Form):
    email = forms.EmailField()

class ForgotPasswordRequestForm(forms.Form):
    email = forms.EmailField()
