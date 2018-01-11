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
            'end_date',
            'city',
            'state',
            'description',
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

VoteParticipantFormSet = forms.modelformset_factory(
    models.VoteParticipant,
    form=VoteParticipantForm,
    extra=1,
    can_delete=True,
)

VoteParticipantInlineFormSet = forms.inlineformset_factory(
    models.Campaign,
    models.VoteParticipant,
    extra=1,
    fields=('name', 'description', 'image',),
    formset=VoteParticipantFormSet,
    min_num=2,
    can_delete=True,
)
