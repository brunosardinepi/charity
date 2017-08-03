from django import forms

from . import models


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='First name')
    last_name = forms.CharField(max_length=100, label='Last name')
    zipcode = forms.CharField(max_length=5, label='Zip code')

    def signup(self, request, user):
        user.save()

        user.userprofile.first_name = self.cleaned_data['first_name']
        user.userprofile.last_name = self.cleaned_data['last_name']
        user.userprofile.zipcode = self.cleaned_data['zipcode']
        user.userprofile.save()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = [
            'first_name',
            'last_name',
            'zipcode',
        ]
