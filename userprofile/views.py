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
    userimages = models.UserImages.objects.filter(user=request.user.id)
    userprofileimage = models.UserImages.objects.filter(user=request.user.id, user_profile=True)
    if userprofile.user == request.user:
        print(userprofile.user_id)
#        print(user_id)
        print(userprofile.user)
        admin_pages = userprofile.page_admins.all()
        manager_pages = userprofile.page_managers.all()
        subscriptions = userprofile.subscribers.all()
        campaigns = userprofile.campaign_admins.all()
        invitations = ManagerInvitation.objects.filter(invite_from=request.user, expired=False)
        form = forms.UserProfileForm(instance=userprofile)
        if request.method == 'POST':
            form = forms.UserProfileForm(
                instance=userprofile,
                data=request.POST,
            )
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(userprofile.get_absolute_url())
        return render(request, 'userprofile/profile.html', {
            'userprofile': userprofile,
            'userimages': userimages,
            'userprofileimage': userprofileimage,
            'admin_pages': admin_pages,
            'manager_pages': manager_pages,
            'subscriptions': subscriptions,
            'campaigns': campaigns,
            'invitations': invitations,
            'form': form,
        })
    else:
        raise Http404

@login_required
def profile_image_upload(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    form = forms.UserImagesForm(instance=userprofile)
    if request.method == 'POST':
        form = forms.UserImagesForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            print("form is valid")
            image = form.cleaned_data.get('image',False)
            image_type = image.content_type.split('/')[0]
            print(image.content_type)
            if image_type in settings.UPLOAD_TYPES:
                if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                    msg = 'The file size limit is %s. Your file size is %s.' % (
                        settings.MAX_IMAGE_UPLOAD_SIZE,
                        image._size
                    )
                    raise ValidationError(msg)
            imageupload = form.save(commit=False)
            imageupload.user_id=request.user.id
            try:
                profile = models.UserImages.objects.get(user=imageupload.user, user_profile=True)
            except models.UserImages.DoesNotExist:
                profile = None
            if profile and imageupload.user_profile:
                profile.user_profile=False
                profile.save()
            imageupload.user_id=request.user.id
            imageupload.save()
        return HttpResponseRedirect(userprofile.get_absolute_url())
    return render(request, 'userprofile/profile_image_upload.html', {'userprofile': userprofile, 'form': form })

