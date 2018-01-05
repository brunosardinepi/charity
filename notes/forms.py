from django import forms


class AbuseCommentForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea)
