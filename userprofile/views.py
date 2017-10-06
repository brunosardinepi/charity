from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

import stripe

from . import forms
from . import models
from donation.models import Donation
from invitations.models import ManagerInvitation
from page import models as PageModels
from pagefund import settings


@login_required
def userprofile(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
        userimages = models.UserImages.objects.filter(user=request.user.id)
        userprofileimage = models.UserImages.objects.filter(user=request.user.id, profile_picture=True)
        admin_pages = userprofile.page_admins.filter(deleted=False)
        manager_pages = userprofile.page_managers.filter(deleted=False)
        subscriptions = userprofile.subscribers.filter(deleted=False)
        campaigns = userprofile.campaign_admins.filter(deleted=False)
        invitations = ManagerInvitation.objects.filter(invite_from=request.user, expired=False)
        donations = Donation.objects.filter(user=request.user)

        cards = {}
        if not settings.TESTING:
            try:
                sc = stripe.Customer.retrieve(userprofile.stripe_customer_id).sources.all(object='card')
                for c in sc:
                    card = get_object_or_404(models.StripeCard, stripe_card_id=c.id)
                    cards[card.id] = {
                        'exp_month': c.exp_month,
                        'exp_year': c.exp_year,
                        'name': card.name,
                        'id': card.id
                    }
            except stripe.error.InvalidRequestError:
                metadata = {'user_pk': request.user.pk}
                customer = stripe.Customer.create(
                    email=request.user.email,
                    metadata=metadata
                )

                request.user.userprofile.stripe_customer_id = customer.id
                request.user.save()

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'state': request.user.userprofile.state,
            'birthday': request.user.userprofile.birthday
        }
        form = forms.UserProfileForm(data)
        if request.method == 'POST':
            form = forms.UserProfileForm(request.POST)
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
            'cards': cards,
            'donations': donations
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
            image = form.cleaned_data.get('image',False)
            image_type = image.content_type.split('/')[0]
            if image_type in settings.UPLOAD_TYPES:
                if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                    return redirect('error:error_image_size')
                imageupload = form.save(commit=False)
                imageupload.user_id=request.user.id
                try:
                    profile = models.UserImages.objects.get(user=imageupload.user, profile_picture=True)
                except models.UserImages.DoesNotExist:
                    profile = None
                if profile and imageupload.profile_picture:
                    profile.profile_picture=False
                    profile.save()
                imageupload.user_id=request.user.id
                imageupload.save()
                return HttpResponseRedirect(userprofile.get_absolute_url())
            else:
                return redirect('error:error_image_type')
    return render(request, 'userprofile/profile_image_upload.html', {'userprofile': userprofile, 'form': form })

@login_required
def user_image_delete(request, image_pk):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    image = get_object_or_404(models.UserImages, pk=image_pk)
    image.delete()
    return HttpResponseRedirect(userprofile.get_absolute_url())
#else:
#    raise Http404

@login_required
def user_profile_update(request, image_pk):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    image = get_object_or_404(models.UserImages, pk=image_pk)
    try:
        profile = models.UserImages.objects.get(user=image.user, profile_picture=True)
    except models.UserImages.DoesNotExist:
        profile = None
    if profile:
        profile.profile_picture = False
        profile.save()
        image.profile_picture = True
        image.save()
    else:
        image.profile_picture = True
        image.save()
    return HttpResponseRedirect(userprofile.get_absolute_url())
#else:
#    raise Http404

@login_required
def update_card(request):
    if request.method == "POST":
        card = get_object_or_404(models.StripeCard, pk=request.POST.get('id'))
        if request.user.userprofile == card.user:
            if "save" in request.POST:
                card.name = request.POST.get('name')
                card.save()
                if not settings.TESTING:
                    customer = stripe.Customer.retrieve(request.user.userprofile.stripe_customer_id)
                    stripe_card = customer.sources.retrieve(card.stripe_card_id)
                    stripe_card.exp_month = request.POST.get('exp_month')
                    stripe_card.exp_year = request.POST.get('exp_year')
                    stripe_card.save()
            elif "delete" in request.POST:
                card.delete()
                if not settings.TESTING:
                    customer = stripe.Customer.retrieve(request.user.userprofile.stripe_customer_id)
                    customer.sources.retrieve(card.stripe_card_id).delete()
            return HttpResponseRedirect(card.user.get_absolute_url())
