from django import forms


class BaseDonate(forms.Form):
    anonymous_amount = forms.BooleanField(required=False)
    anonymous_donor = forms.BooleanField(required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)
    amount = forms.IntegerField()

class DonateForm(BaseDonate):
    monthly = forms.BooleanField(required=False)

class DonateUnauthenticatedForm(BaseDonate):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
