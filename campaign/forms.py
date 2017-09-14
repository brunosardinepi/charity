from django import forms

from . import models


class CampaignForm(forms.ModelForm):
    class Meta:
        model = models.Campaign
        fields = [
            'name',
            'campaign_slug',
            'type',
            'goal',
            'city',
            'description',
            'campaign_icon',
        ]

class DeleteCampaignForm(forms.ModelForm):
    class Meta:
        model = models.Campaign
        fields = ['name']

class ManagerInviteForm(forms.Form):
    email = forms.EmailField()
    manager_edit = forms.BooleanField(required=False, label='Edit Campaign')
    manager_delete = forms.BooleanField(required=False, label='Delete Campaign')
    manager_invite = forms.BooleanField(required=False, label='Invite users to manage Campaign')
