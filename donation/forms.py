from django import forms


class DonateForm(forms.Form):
    anonymous_amount = forms.BooleanField(required=False)
    anonymous_donor = forms.BooleanField(required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)
    amount = forms.IntegerField()
    cover_fees = forms.BooleanField(required=False)
    save_card = forms.BooleanField(required=False)

