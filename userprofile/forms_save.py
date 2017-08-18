from django import forms
from django.core.files.images import get_image_dimensions
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
            avatar = self.cleaned_data.get('avatar',False)

            try:
                w, h = get_image_dimensions(avatar)

                #validate dimensions
                max_width = max_height = 100
                if w > max_width or h > max_height:
                    raise forms.ValidationError(
                        u'Please use an image that is '
                        '%s x %s pixels or smaller.' % (max_width, max_height))

                #validate content type
                main, sub = avatar.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                    raise forms.ValidationError(u'Please use a JPEG, '
                        'GIF or PNG image.')

                #validate file size
                if len(avatar) > (20 * 1024):
                    raise forms.ValidationError(
                        u'Avatar file size may not exceed 20k.')

            except AttributeError:
                #Handles case when we are updating the user profile and do not supply a new avatar
                pass

            return avatar
        model = models.UserProfile
        fields = [
            'first_name',
            'last_name',
            'zipcode',
            'avatar',
        ]
