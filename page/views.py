import json

from time import strftime

from collections import OrderedDict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View

import stripe
from guardian.shortcuts import assign_perm, get_user_perms, remove_perm

from . import forms
from .models import Page, PageImage
from .utils import campaign_average_duration, campaign_types
from campaign.models import Campaign
from comments.forms import CommentForm
from comments.models import Comment
from donation.forms import DonateForm
from donation.models import Donation
from donation.utils import donate, donation_graph, donation_history, donation_statistics
from invitations.models import ManagerInvitation
from invitations.utils import invite
from userprofile.utils import get_user_credit_cards
from userprofile import models as UserProfileModels
from pagefund import config, settings, utils
from pagefund.image import image_is_valid
from plans.models import StripePlan


stripe.api_key = config.settings['stripe_api_sk']

def page(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    if page.deleted == True:
        raise Http404
    else:
        form = CommentForm
        donate_form = DonateForm()
        template_params = {}

        if request.user.is_authenticated:
            cards = get_user_credit_cards(request.user.userprofile)
            template_params["cards"] = cards

        try:
            user_subscription_check = page.subscribers.get(user_id=request.user.pk)
        except UserProfileModels.UserProfile.DoesNotExist:
            user_subscription_check = None

        if user_subscription_check:
            subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
        else:
            subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}

        if request.method == "POST":
             utils.update_manager_permissions(request.POST.getlist('permissions[]'), page)

        template_params["page"] = page
        template_params["form"] = form
        template_params["donate_form"] = donate_form
        template_params["subscribe_attr"] = subscribe_attr
        template_params["api_pk"] = config.settings['stripe_api_pk']
        return render(request, 'page/page.html', template_params)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required(login_url='signup')
def page_create(request):
    page_form = forms.PageForm()
    bank_form = forms.PageBankForm()
    if request.method == 'POST':
        page_form = forms.PageForm(request.POST)
        bank_form = forms.PageBankForm(request.POST)
        if page_form.is_valid() and bank_form.is_valid():
            page = page_form.save()
            page.admins.add(request.user.userprofile)
            page.subscribers.add(request.user.userprofile)

            if not settings.TESTING:
                if page.type == 'personal':
                    stripe_type = 'individual'
                else:
                    stripe_type = 'company'

                legal_entity = {
                    "business_name": page.name,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "type": stripe_type,
                    "dob": {
                        "day": request.user.userprofile.birthday.day,
                        "month": request.user.userprofile.birthday.month,
                        "year": request.user.userprofile.birthday.year
                    },
                    "address": {
                        "city": page.city,
                        "line1": page.address_line1,
                        "line2": page.address_line2,
                        "postal_code": page.zipcode,
                        "state": page.state
                    },
                    "business_tax_id": page.ein,
                    "ssn_last_4": page_form.cleaned_data['ssn']
                }

                if page_form.cleaned_data['tos_acceptance'] == True:
                    user_ip = get_client_ip(request)
                    tos_acceptance = {
                        "date": timezone.now(),
                        "ip": user_ip
                    }

                    acct = stripe.Account.create(
                        business_name=page.name,
                        country="US",
                        email=request.user.email,
                        legal_entity=legal_entity,
                        type="custom",
                        tos_acceptance=tos_acceptance
                    )

                external_account = {
                    "object": "bank_account",
                    "country": "US",
                    "account_number": bank_form.cleaned_data['account_number'],
                    "account_holder_name": "%s %s" % (request.user.first_name, request.user.last_name),
                    "account_holder_type": stripe_type,
                    "routing_number": bank_form.cleaned_data['routing_number']
                }
                ext_acct = acct.external_accounts.create(external_account=external_account)
                page.stripe_account_id = acct.id
                page.stripe_bank_account_id = ext_acct.id
            page.save()

            subject = "Page created!"
            body = "You just created a Page for: %s" % page.name
            utils.email(request.user.email, subject, body)
            return HttpResponseRedirect(page.get_absolute_url())
    return render(request, 'page/page_create.html', {'page_form': page_form, 'bank_form': bank_form})

@login_required
def page_edit(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    admin = request.user.userprofile in page.admins.all()
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_edit', page):
        manager = True
    else:
        manager = False
    if admin or manager:
        form = forms.PageForm(instance=page)
        if request.method == 'POST':
            form = forms.PageForm(instance=page, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'page/page_edit.html', {'page': page, 'page_form': form})

@login_required
def page_delete(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    admin = request.user.userprofile in page.admins.all()
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_delete', page):
        manager = True
    else:
        manager = False
    if admin or manager:
        page.deleted = True
        page.deleted_by = request.user
        page.deleted_on = timezone.now()
        page.name = page.name + "_deleted_" + timezone.now().strftime("%Y%m%d")
        page.page_slug = page.page_slug + "deleted" + timezone.now().strftime("%Y%m%d")
        page.save()

        campaigns = Campaign.objects.filter(page=page, deleted=False)
        if campaigns:
            for c in campaigns:
                c.deleted = True
                c.deleted_by = request.user
                c.deleted_on = timezone.now()
                c.name = c.name + "_deleted_" + timezone.now().strftime("%Y%m%d")
                c.campaign_slug = c.campaign_slug + "deleted" + timezone.now().strftime("%Y%m%d")
                c.save()

        if not settings.TESTING:
            account = stripe.Account.retrieve(page.stripe_account_id)
            account.delete()

        return HttpResponseRedirect(reverse('home'))
    else:
        raise Http404

@login_required
def subscribe(request, page_pk, action=None):
    page = get_object_or_404(Page, pk=page_pk)
    if action == "subscribe":
        page.subscribers.add(request.user.userprofile)
        new_subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
    elif action == "unsubscribe":
        page.subscribers.remove(request.user.userprofile)
        new_subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}
    else:
        print("something went wrong")
    new_subscribe_attr = json.dumps(new_subscribe_attr)
    return HttpResponse(new_subscribe_attr)

@login_required
def page_invite(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    # True if the user is an admin
    admin = request.user.userprofile in page.admins.all()
    # True if the user is a manager and has the 'invite' permission
    if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_invite', page):
        manager = True
    else:
        manager = False
    # if the user is either an admin or a manager, so either must be True
    if admin or manager:
        form = forms.ManagerInviteForm()
        if request.method == 'POST':
            form = forms.ManagerInviteForm(request.POST)
            if form.is_valid():
                data = {
                    "request": request,
                    "form": form,
                    "page": page,
                    "campaign": None
                }

                status = invite(data)
                if status == True:
                    # redirect the admin/manager to the Page
                    return HttpResponseRedirect(page.get_absolute_url())
        return render(request, 'page/page_invite.html', {'form': form, 'page': page})
    # the user isn't an admin or a manager, so they can't invite someone
    # the only way someone got here was by typing the url manually
    else:
        raise Http404

@login_required
def remove_manager(request, page_slug, manager_pk):
    page = get_object_or_404(Page, page_slug=page_slug)
    manager = get_object_or_404(User, pk=manager_pk)
    # only page admins can remove managers
    if request.user.userprofile in page.admins.all():
        # remove the manager
        page.managers.remove(manager.userprofile)
        # revoke the permissions
        remove_perm('manager_edit', manager, page)
        remove_perm('manager_delete', manager, page)
        remove_perm('manager_invite', manager, page)
        remove_perm('manager_image_edit', manager, page)
        # redirect to page
        return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404


class PageImageUpload(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        admin = request.user.userprofile in page.admins.all()
        if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_image_edit', page):
            manager = True
        else:
            manager = False
        if admin or manager:
            images = PageImage.objects.filter(page=page)
            return render(self.request, 'page/images.html', {'page': page, 'images': images})
        else:
            raise Http404

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        admin = request.user.userprofile in page.admins.all()
        if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_image_edit', page):
            manager = True
        else:
            manager = False
        if admin or manager:
            form = forms.PageImageForm(self.request.POST, self.request.FILES)
            data = image_is_valid(request, form, page)
            return JsonResponse(data)
        else:
            raise Http404

def page_donate(request, page_pk):
    page = get_object_or_404(Page, pk=page_pk)
    if request.method == "POST":
        form = DonateForm(request.POST)
        if form.is_valid():
            donate(request=request, form=form, page=page, campaign=None)
            return HttpResponseRedirect(page.get_absolute_url())

@login_required
def page_image_delete(request, image_pk):
    image = get_object_or_404(PageImage, pk=image_pk)
    admin = request.user.userprofile in image.page.admins.all()
    if request.user.userprofile in image.page.managers.all() and request.user.has_perm('manager_image_edit', image.page):
        manager = True
    else:
        manager = False
    if admin or manager:
        image.delete()
        return HttpResponse('')
    else:
        raise Http404

@login_required
def page_profile_update(request, image_pk):
    image = get_object_or_404(PageImage, pk=image_pk)
    admin = request.user.userprofile in image.page.admins.all()
    if request.user.userprofile in image.page.managers.all() and request.user.has_perm('manager_image_edit', image.page):
        manager = True
    else:
        manager = False
    if admin or manager:
        try:
            profile_picture = PageImage.objects.get(page=image.page, profile_picture=True)
        except PageImage.DoesNotExist:
            profile_picture = None
        if profile_picture:
            profile_picture.profile_picture = False
            profile_picture.save()
        image.profile_picture = True
        image.save()
        return HttpResponse('')
    else:
        raise Http404

class PageDashboard(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        admin = request.user.userprofile in page.admins.all()
        if request.user.userprofile in page.managers.all() and request.user.has_perm('manager_view_dashboard', page):
            manager = True
        else:
            manager = False
        if admin or manager:
            return render(self.request, 'page/dashboard.html', {
                'page': page,
                'donations': donation_statistics(page),
                'graph': donation_graph(page, 30),
                'campaign_types': campaign_types(page),
                'campaign_average_duration': campaign_average_duration(page)
            })
        else:
            raise Http404

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        utils.update_manager_permissions(request.POST.getlist('permissions[]'), page)
        return render(self.request, 'page/dashboard.html', {'page': page})
