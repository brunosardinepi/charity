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
            'description',
        ]

class DeleteCampaignForm(forms.ModelForm):
    class Meta:
        model = models.Campaign
        fields = ['name']
