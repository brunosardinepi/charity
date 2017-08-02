from django import forms

from . import models


class SignupForm(forms.Form):
    zipcode = forms.CharField(max_length=5, label='Zip code')

    def signup(self, request, user):
        user.save()

        user.profile.zipcode = self.cleaned_data['zipcode']
        user.profile.save()
