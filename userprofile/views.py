from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from . import forms
from . import models
from page import models as PageModels


@login_required
def userprofile(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    subscriptions = userprofile.subscribers.all()
    campaigns = request.user.campaign_set.all()
    if userprofile.user == request.user:
        form = forms.UserProfileForm(instance=userprofile)
        if request.method == 'POST':
            form = forms.UserProfileForm(instance=userprofile, data=request.POST, files=request.FILES)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                zipcode = form.cleaned_data['zipcode']
                avatar = form.cleaned_data['avatar']
                form.save()
    return render(request, 'userprofile/profile.html', {'subscriptions': subscriptions, 'campaigns': campaigns, 'form': form})
