from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from . import models
from invitations.models import ManagerInvitation
from page import models as PageModels


@login_required
def userprofile(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
        admin_pages = userprofile.page_admins.filter(deleted=False)
        manager_pages = userprofile.page_managers.filter(deleted=False)
        subscriptions = userprofile.subscribers.filter(deleted=False)
        campaigns = userprofile.campaign_admins.filter(deleted=False)
        invitations = ManagerInvitation.objects.filter(invite_from=request.user, expired=False)
        form = forms.UserProfileForm(instance=userprofile)
        if request.method == 'POST':
            form = forms.UserProfileForm(
                instance=userprofile,
                data=request.POST,
                files=request.FILES
            )
            if form.is_valid():
                image = form.cleaned_data.get('avatar',False)
                image_type = image.content_type.split('/')[0]
                if image_type in settings.UPLOAD_TYPES:
                    if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                        return redirect('error:error_image_size')
                    form.save()
                    return HttpResponseRedirect(userprofile.get_absolute_url())
        return render(request, 'userprofile/profile.html', {
            'admin_pages': admin_pages,
            'manager_pages': manager_pages,
            'subscriptions': subscriptions,
            'campaigns': campaigns,
            'invitations': invitations,
            'form': form
        })
    else:
        raise Http404
