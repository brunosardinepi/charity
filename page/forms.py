from datetime import datetime

from django import forms

from . import models
from userprofile.widgets import CustomSelectDateWidget


class PageForm1(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm1, self).__init__(*args, **kwargs)
        self.fields['tos_accepted'].required = True

    class Meta:
        model = models.Page
        fields = [
            'name',
            'type',
            'category',
            'description',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'zipcode',
            'tos_accepted',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Page name'}),
            'address_line1': forms.TextInput(attrs={'placeholder': '123 Main St.'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Suite 200 (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'zipcode': forms.TextInput(attrs={'placeholder': '12345'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'Tell the world about your Page! (optional)',
                'rows': 8,
            }),
        }


class PageForm2(forms.Form):
    first_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    YEAR_CHOICES = list(range(1900, datetime.now().year))[::-1]
    birthday = forms.DateField(widget=CustomSelectDateWidget(years=YEAR_CHOICES), initial='1990-06-14')

class PageForm3(forms.Form):
    ein = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': '000000001'}))

class PageForm4(forms.Form):
    ssn = forms.CharField(max_length=4, label="Last 4 of SSN", widget=forms.TextInput(attrs={'placeholder': '0000'}))
    account_number = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'placeholder': '000123456789'}))
    routing_number = forms.CharField(max_length=9, widget=forms.TextInput(attrs={'placeholder': '110000000'}))

class PageEditForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = [
            'name',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'zipcode',
            'page_slug',
            'type',
            'category',
            'description',
            'website',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'PageFund'}),
            'page_slug': forms.TextInput(attrs={'placeholder': 'pagefund'}),
            'website': forms.TextInput(attrs={'placeholder': 'https://page.fund'}),
            'address_line1': forms.TextInput(attrs={'placeholder': '123 Main St.'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Suite 200'}),
            'description': forms.Textarea(attrs={'placeholder': 'We are an amazing group that does amazing things!'}),
        }

class PageImageForm(forms.ModelForm):
    class Meta:
        model = models.PageImage
        fields = [
            'image',
            'caption',
            'profile_picture'
        ]

class DeletePageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ['name']

class ManagerInviteForm(forms.Form):
    email = forms.EmailField()
    manager_edit = forms.BooleanField(required=False, label='Edit Page')
    manager_delete = forms.BooleanField(required=False, label='Delete Page')
    manager_invite = forms.BooleanField(required=False, label='Invite users to manage Page')
    manager_image_edit = forms.BooleanField(required=False, label='Upload image')
    manager_view_dashboard = forms.BooleanField(required=False, label='View dashboard')

class PageBankForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

    YEAR_CHOICES = list(range(1900, datetime.now().year))[::-1]
    birthday = forms.DateField(required=False, widget=CustomSelectDateWidget(years=YEAR_CHOICES))
#    account_holder_first_name = forms.CharField(max_length=255)
#    account_holder_last_name = forms.CharField(max_length=255)
    ssn = forms.CharField(max_length=4, label="Last 4 of SSN")
    account_number = forms.CharField(max_length=12)
    routing_number = forms.CharField(max_length=9)

class PageBankEINForm(PageBankForm):
    ein = forms.CharField(max_length=20)

class PageEditBankForm(forms.Form):
    ssn = forms.CharField(max_length=4, label="Last 4 of SSN")
    account_number = forms.CharField(max_length=12)
    routing_number = forms.CharField(max_length=9)

class PageEditBankEINForm(PageEditBankForm):
    ein = forms.CharField(max_length=20)
