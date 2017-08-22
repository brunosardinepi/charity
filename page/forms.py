from django import forms

from . import models


class PageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = [
            'name',
            'page_slug',
            'category',
            'description',
        ]

class DeletePageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ['name']

class ManagerInviteForm(forms.Form):
    email = forms.EmailField()
    can_edit = forms.BooleanField(required=False)
    can_delete = forms.BooleanField(required=False)
    can_invite = forms.BooleanField(required=False)
