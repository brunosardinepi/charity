from django import forms

from . import models


class PageForm(forms.ModelForm):
    ssn = forms.CharField(max_length=9)

    class Meta:
        model = models.Page
        fields = [
            'name',
            'ein',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'zipcode',
            'page_slug',
            'type',
            'category',
            'description'
        ]

class PageImagesForm(forms.ModelForm):
    class Meta:
        model = models.PageImages
        fields = [
            'image',
            'caption',
            'page_profile'
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
    manager_upload = forms.BooleanField(required=False, label='Upload image')
