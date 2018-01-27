from django.forms.widgets import ClearableFileInput


class VoteParticipantInput(ClearableFileInput):
    template_name = 'campaign/voteparticipant_input.html'
