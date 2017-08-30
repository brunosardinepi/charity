from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from . import forms
from . import models
from invitations.models import ManagerInvitation
from page import models as PageModels


@login_required
def userprofile(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
        subscriptions = userprofile.subscribers.all()
        campaigns = request.user.campaign_set.all()
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
                        msg = 'The file size limit is %s. Your file size is %s.' % (
                            settings.MAX_IMAGE_UPLOAD_SIZE,
                            image._size
                        )
                        raise ValidationError(msg)
                    form.save()
                    return HttpResponseRedirect(userprofile.get_absolute_url())
        return render(request, 'userprofile/profile.html', {
            'subscriptions': subscriptions,
            'campaigns': campaigns,
            'invitations': invitations,
            'form': form
        })
    else:
        raise Http404
