from django import forms


class AbuseForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea)
