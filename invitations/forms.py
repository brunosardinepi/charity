from django import forms


class ForgotPasswordRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))

class ForgotPasswordResetForm(forms.Form):
    password1 = forms.CharField(max_length=255, label='Password')
    password2 = forms.CharField(max_length=255, label='Password (again)')

    def clean(self):
        data = self.cleaned_data
        if "password1" in data and "password2" in data:
            if data["password1"] != data["password2"]:
                self._errors["password2"] = self.error_class(['Passwords do not match.'])
                del data['password2']
        return data
