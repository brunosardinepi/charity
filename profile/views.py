from django.shortcuts import get_object_or_404, render

from . import forms
from . import models


def profile(request):
    user_profile = get_object_or_404(models.Profile, user_id=request.user.id)
    if user_profile.user == request.user:
        form = forms.ProfileForm(instance=user_profile)
        if request.method == 'POST':
            form = forms.ProfileForm(instance=user_profile, data=request.POST)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                zipcode = form.cleaned_data['zipcode']
                form.save()
    return render(request, 'profile/profile.html', {'form': form})
