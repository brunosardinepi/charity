from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

import stripe

from . import forms
from .models import StripeCard, UserImage, UserProfile
from .utils import get_user_credit_cards
from donation.models import Donation
from invitations.models import ManagerInvitation
from page import models as PageModels
from pagefund import config, settings
from pagefund.image import image_is_valid


@login_required
def userprofile(request):
    userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
        cards = get_user_credit_cards(userprofile)

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
            'form': form,
            'cards': cards,
            'api_pk': config.settings['stripe_api_pk']
        })
    else:
        raise Http404

class UserImageUpload(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        images = UserImage.objects.filter(user=userprofile)
        return render(self.request, 'userprofile/images.html', {'userprofile': userprofile, 'images': images})

    def post(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        form = forms.UserImageForm(self.request.POST, self.request.FILES)
        data = image_is_valid(request, form, userprofile)
        return JsonResponse(data)

@login_required
def user_image_delete(request, image_pk):
    # needs test
    image = get_object_or_404(UserImage, pk=image_pk)
    if request.user.userprofile == image.user:
        image.delete()
        return HttpResponse('')
    else:
        raise Http404

@login_required
def user_profile_update(request, image_pk):
    userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
    image = get_object_or_404(UserImage, pk=image_pk)
    if image.user == request.user.userprofile:
        try:
            profile_picture = UserImage.objects.get(user=image.user, profile_picture=True)
        except UserImage.DoesNotExist:
            profile_picture = None
        if profile_picture:
            profile_picture.profile_picture = False
            profile_picture.save()
        image.profile_picture = True
        image.save()
        return HttpResponse('')
    else:
        raise Http404

@login_required
def add_card(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)

            customer_cards = request.user.userprofile.stripecard_set.all()
            card_check = stripe.Token.retrieve(request.POST.get('stripeToken'))
            customer_card_dict = {}
            if customer_cards:
                for c in customer_cards:
                    if c.stripe_card_fingerprint == card_check['card']['fingerprint']:
                        card_source = c.stripe_card_id
                        break
                    else:
                        card_source = None
            else:
                card_source = None
            if card_source is None:
                card_source = customer.sources.create(source=request.POST.get('stripeToken'))
                StripeCard.objects.create(
                    user=request.user.userprofile,
                    stripe_card_id=card_source.id,
                    stripe_card_fingerprint=card_source.fingerprint
                )
            return HttpResponseRedirect(request.user.userprofile.get_absolute_url())

@login_required
def update_card(request):
    if request.method == "POST":
        card = get_object_or_404(StripeCard, pk=request.POST.get('id'))
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
