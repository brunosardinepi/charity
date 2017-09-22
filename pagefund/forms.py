from django import forms


class GeneralInviteForm(forms.Form):
    email = forms.EmailField()
