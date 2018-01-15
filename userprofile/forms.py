from datetime import datetime

from django import forms

from . import models


YEAR_CHOICES = list(range(1900, datetime.now().year))[::-1]

class UserProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='First name', required=False)
    last_name = forms.CharField(max_length=100, label='Last name', required=False)
    birthday = forms.DateField(required=False, widget=forms.SelectDateWidget(years=YEAR_CHOICES))
    STATE_CHOICES = (
        ('', '-----'),
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    )
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        label='State',
        required=False,
    )

    def signup(self, request, user):
        user.save()

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.userprofile.state = self.cleaned_data['state']
        user.userprofile.birthday = self.cleaned_data['birthday']

        user.save()
        user.userprofile.save()


class UserImageForm(forms.ModelForm):
    class Meta:
        model = models.UserImage
        fields = [
            'image',
            'caption',
            'profile_picture',
        ]
