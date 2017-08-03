from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from . import forms
from . import models


@login_required
def userprofile(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
        form = forms.UserProfileForm(instance=userprofile)
        if request.method == 'POST':
            form = forms.UserProfileForm(instance=userprofile, data=request.POST)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                zipcode = form.cleaned_data['zipcode']
                form.save()
    return render(request, 'userprofile/profile.html', {'form': form})
