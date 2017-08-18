from django import forms
from django.core.files.images import get_image_dimensions
from PIL import Image
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
        def clean_avatar(self):
            CONTENT_TYPES = ['image']
            MAX_UPLOAD_PHOTO_SIZE = ['260']
            avatar = self.cleaned_data.get('avatar',False)
            if content._size > MAX_UPLOAD_PHOTO_SIZE:
                msg = 'Keep your file size under %s. actual size %s'\
                        % (filesizeformat(settings.MAX_UPLOAD_PHOTO_SIZE), filesizeformat(content._size))
                raise forms.ValidationError(msg)
            return avatar
        model = models.UserProfile
        fields = [
            'first_name',
            'last_name',
            'zipcode',
            'avatar',
        ]
