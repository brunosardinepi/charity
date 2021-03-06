import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from sendgrid.helpers.mail import *
import sendgrid
import stripe

from . import forms
from .models import StripeCard, UserImage, UserProfile
from .utils import get_last4_donation, get_user_credit_cards
from donation.models import Donation
from notes.utils import create_error
from invitations.models import ManagerInvitation
from page import models as PageModels
from pagefund import config, settings
from pagefund.image import image_is_valid


@login_required
def userprofile(request):
    userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
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
                request.user.first_name = form.cleaned_data["first_name"]
                request.user.last_name = form.cleaned_data["last_name"]
                userprofile.birthday = form.cleaned_data["birthday"]
                userprofile.state = form.cleaned_data["state"]
                request.user.save()
                userprofile.save()

                try:
                    data = [
                      {
                        'email': request.user.email,
                        'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                      }
                    ]
                    sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
                    response = sg.client.contactdb.recipients.patch(request_body=data)
                except:
                    pass

                messages.success(request, 'Profile updated')
                return HttpResponseRedirect(userprofile.get_absolute_url())
        return render(request, 'userprofile/profile.html', {
            'userprofile': userprofile,
            'form': form,
            'api_pk': config.settings['stripe_api_pk'],
        })
    else:
        raise Http404

class UserImageUpload(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        images = UserImage.objects.filter(user=userprofile).order_by('-date')
        return render(self.request, 'userprofile/images.html', {'userprofile': userprofile, 'images': images})

    def post(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        form = forms.UserImageForm(self.request.POST, self.request.FILES)
        data = image_is_valid(request, form, userprofile)
        if data:
            return JsonResponse(data)
        else:
            return HttpResponse('')

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
                messages.success(request, 'Card added')
            else:
                messages.error(request, 'Card already exists')
            return HttpResponseRedirect(reverse('userprofile:billing'))

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
                messages.success(request, 'Card saved')
            elif "delete" in request.POST:
                card.delete()
                if not settings.TESTING:
                    customer = stripe.Customer.retrieve(request.user.userprofile.stripe_customer_id)
                    customer.sources.retrieve(card.stripe_card_id).delete()
                messages.success(request, 'Card deleted')
            return HttpResponseRedirect(reverse('userprofile:billing'))

class Notifications(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)
        return render(request, 'userprofile/notifications.html', {'userprofile': userprofile})

    def post(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)
        post_data = request.POST.getlist('notification_preferences[]')
        new_notification_preferences = [n for n in post_data]
        old_notification_preferences = userprofile.notification_preferences()
        for o in old_notification_preferences:
            if o in new_notification_preferences:
                setattr(userprofile, "%s" % o, True)
            else:
                setattr(userprofile, "%s" % o, False)
        userprofile.save()
        messages.success(request, 'Notifications updated')
        return HttpResponseRedirect(reverse('userprofile:notifications'))


def card_list(request):
    cards = get_user_credit_cards(request.user.userprofile)
    return HttpResponse(
        json.dumps(cards),
        content_type="application/json"
    )

class UserProfileTaxes(View):
    def get(self, request):
        donations = {}
        donation_queryset = Donation.objects.filter(user=request.user)
        for donation in donation_queryset:
            donations[donation.pk] = {
                "page": donation.page,
                "date": donation.date,
                "amount": donation.amount,
                "last4": get_last4_donation(donation),
            }
        return render(request, 'userprofile/taxes.html', {"donations": donations})

class PagesCampaigns(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        return render(self.request, 'userprofile/pages_campaigns.html', {'userprofile': userprofile})

class PendingInvitations(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        invitations = ManagerInvitation.objects.filter(
            invite_to=request.user.email,
            expired=False,
            accepted=False,
            declined=False,
        )
        return render(request, 'userprofile/pending_invitations.html', {
            'userprofile': userprofile,
            'invitations': invitations,
        })

class Donations(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        return render(self.request, 'userprofile/donations.html', {'userprofile': userprofile})

class Billing(View):
    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
        if userprofile.user == request.user:
            try:
                cards = get_user_credit_cards(userprofile)
                stripe_error = None
            except Exception as e:
                cards = None
                stripe_error = True
                create_error(e, request)

        return render(request, 'userprofile/billing.html', {
            'userprofile': userprofile,
            'cards': cards,
            'stripe_error': stripe_error,
            'api_pk': config.settings['stripe_api_pk'],
        })
