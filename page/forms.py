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
            'description': forms.Textarea(attrs={'rows': 8}),
        }


class PageForm2(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    YEAR_CHOICES = list(range(1900, datetime.now().year))[::-1]
    birthday = forms.DateField(widget=CustomSelectDateWidget(years=YEAR_CHOICES), initial='1990-06-14')

class PageForm3(forms.Form):
    ein = forms.CharField(max_length=20)

class PageForm4(forms.Form):
    ssn = forms.CharField(max_length=4)
    account_number = forms.CharField(max_length=20)
    routing_number = forms.CharField(max_length=9)

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
    ssn = forms.CharField(max_length=4)
    account_number = forms.CharField(max_length=12)
    routing_number = forms.CharField(max_length=9)

class PageBankEINForm(PageBankForm):
    ein = forms.CharField(max_length=20)

class PageEditBankForm(forms.Form):
    ssn = forms.CharField(max_length=4)
    account_number = forms.CharField(max_length=12)
    routing_number = forms.CharField(max_length=9)

class PageEditBankEINForm(PageEditBankForm):
    ein = forms.CharField(max_length=20)

class PageUnverifiedEditBankForm(forms.Form):
    ssn = forms.CharField(max_length=9)
    account_number = forms.CharField(max_length=12)
    routing_number = forms.CharField(max_length=9)

class PageUnverifiedEditBankEINForm(forms.Form):
    ssn = forms.CharField(max_length=9)
    account_number = forms.CharField(max_length=12)
    routing_number = forms.CharField(max_length=9)
    ein = forms.CharField(max_length=20)