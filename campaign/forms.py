from django import forms

from . import models
from .widgets import VoteParticipantInput


class CampaignForm(forms.ModelForm):
    class Meta:
        model = models.Campaign
        fields = [
            'name',
            'campaign_slug',
            'type',
            'goal',
            'end_date',
            'category',
            'description',
            'website',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Fun Run for the Cure'}),
            'campaign_slug': forms.TextInput(attrs={'placeholder': 'funrunforthecure'}),
            'website': forms.TextInput(attrs={'placeholder': 'http://funrunforthecure.com'}),
            'description': forms.Textarea(attrs={'placeholder': 'Help us raise money during our Fun Run for the Cure!'}),
            'goal': forms.NumberInput(attrs={'placeholder': '5000'}),
        }

class DeleteCampaignForm(forms.ModelForm):
    class Meta:
        model = models.Campaign
        fields = ['name']

class ManagerInviteForm(forms.Form):
    email = forms.EmailField()
    manager_edit = forms.BooleanField(required=False, label='Edit Campaign')
    manager_delete = forms.BooleanField(required=False, label='Delete Campaign')
    manager_invite = forms.BooleanField(required=False, label='Invite users to manage Campaign')
    manager_image_edit = forms.BooleanField(required=False, label='Upload image')
    manager_view_dashboard = forms.BooleanField(required=False, label='View dashboard')

class CampaignImageForm(forms.ModelForm):
    class Meta:
        model = models.CampaignImage
        fields = [
            'image',
            'caption',
            'profile_picture',
        ]

class CampaignSearchPagesForm(forms.Form):
    page = forms.CharField(max_length=255)

class VoteParticipantForm(forms.ModelForm):
    class Meta:
        model = models.VoteParticipant
        fields = [
            'name',
            'description',
            'image',
        ]
        widgets = {
            'image': VoteParticipantInput(),
            'description': forms.Textarea(attrs={'rows': 5}),
        }

VoteParticipantFormSet = forms.modelformset_factory(
    models.VoteParticipant,
    form=VoteParticipantForm,
    widgets = {
        'image': VoteParticipantInput(),
        'description': forms.Textarea(attrs={'rows': 5}),
    },
    extra=1,
    can_delete=True,
)

VoteParticipantInlineFormSet = forms.inlineformset_factory(
    models.Campaign,
    models.VoteParticipant,
    extra=1,
    fields=('name', 'description', 'image',),
    formset=VoteParticipantFormSet,
    widgets = {
        'image': VoteParticipantInput(),
        'description': forms.Textarea(attrs={'rows': 5}),
    },
    min_num=2,
    can_delete=True,
)
