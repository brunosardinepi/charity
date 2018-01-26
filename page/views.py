import json
import operator

from datetime import timezone
from time import strftime

from collections import OrderedDict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View

import stripe
from guardian.shortcuts import assign_perm, get_user_perms, remove_perm

from . import forms
from .models import Page, PageImage
from .utils import campaign_average_duration, campaign_success_pct, campaign_types
from campaign.models import Campaign
from comments.forms import CommentForm
from donation.forms import DonateForm, DonateUnauthenticatedForm
from donation.models import Donation
from donation.utils import donate, donation_graph, donation_history, donation_statistics
from notes.utils import create_error, error_email
from invitations.models import ManagerInvitation
from invitations.utils import invite
from userprofile.models import UserProfile
from userprofile.utils import get_user_credit_cards
from pagefund import config, settings, utils
from pagefund.image import image_is_valid
from plans.models import StripePlan


stripe.api_key = config.settings['stripe_api_sk']

def page(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    template_params = {}

    if page.deleted == True:
        raise Http404
    else:
        if request.user.is_authenticated():
            donate_form = DonateForm()
            template_params["form"] = CommentForm
        else:
            donate_form = DonateUnauthenticatedForm()

        try:
            user_subscription_check = page.subscribers.get(user_id=request.user.pk)
        except UserProfile.DoesNotExist:
            user_subscription_check = None

        if user_subscription_check:
            subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe"}
        else:
            subscribe_attr = {"name": "subscribe", "value": "Subscribe"}

        template_params["page"] = page
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
    form = forms.PageForm()
    if request.method == 'POST':
        form = forms.PageForm(request.POST)
        if form.is_valid():
            page = form.save()
            page.admins.add(request.user.userprofile)
            page.subscribers.add(request.user.userprofile)
            if request.user.first_name and request.user.last_name and request.user.userprofile.birthday:
                return redirect('page_create_bank_info', page_slug=page.page_slug)
            else:
                return redirect('page_create_additional_info', page_slug=page.page_slug)
    return render(request, 'page/page_create.html', {'form': form})


class PageCreateAdditionalInfo(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        userprofile = get_object_or_404(UserProfile, user=request.user)
        initial = {
            'first_name': userprofile.user.first_name,
            'last_name': userprofile.user.last_name,
            'birthday': userprofile.birthday,
        }
        form = forms.PageAdditionalInfoForm(initial=initial)
        return render(request, 'page/page_create_additional_info.html', {'page': page, 'form': form})
    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        userprofile = get_object_or_404(UserProfile, user=request.user)
        form = forms.PageAdditionalInfoForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            userprofile.birthday = form.cleaned_data['birthday']
            userprofile.save()
            return redirect('page_create_bank_info', page_slug=page.page_slug)


class PageCreateBankInfo(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        userprofile = get_object_or_404(UserProfile, user=request.user)
        initial = {
            'account_holder_first_name': userprofile.user.first_name,
            'account_holder_last_name': userprofile.user.last_name,
        }
        form = forms.PageBankForm(initial=initial)
        return render(request, 'page/page_create_bank_info.html', {'page': page, 'form': form})

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        form = forms.PageBankForm(request.POST)
        if form.is_valid():
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
                    "ssn_last_4": form.cleaned_data['ssn']
                }

                user_ip = get_client_ip(request)
                tos_acceptance = {
                    "date": timezone.now(),
                    "ip": user_ip
                }

                try:
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
                        "account_number": form.cleaned_data['account_number'],
                        "account_holder_name": "%s %s" % (request.user.first_name, request.user.last_name),
                        "account_holder_type": stripe_type,
                        "routing_number": form.cleaned_data['routing_number'],
                        "default_for_currency": "true",
                    }
                    ext_acct = acct.external_accounts.create(external_account=external_account)
                except stripe.error.InvalidRequestError as e:
                    error = create_error(e, request, page)
                    page.delete()
                    return redirect('error:error_stripe_invalid_request', error_pk=error.pk)

                page.stripe_account_id = acct.id
                page.stripe_bank_account_id = ext_acct.id
            page.save()

            utils.email(request.user.email, "blank", "blank", "new_page_created")
            return HttpResponseRedirect(page.get_absolute_url())


class PageEditBankInfo(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        userprofile = get_object_or_404(UserProfile, user=request.user)
        initial = {
            'account_holder_first_name': userprofile.user.first_name,
            'account_holder_last_name': userprofile.user.last_name,
        }
        form = forms.PageEditBankForm(initial=initial)
        return render(request, 'page/page_edit_bank_info.html', {'page': page, 'form': form})

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        form = forms.PageEditBankForm(request.POST)
        if form.is_valid():
            if not settings.TESTING:

                if page.type == 'personal':
                    stripe_type = 'individual'
                else:
                    stripe_type = 'company'

                acct = stripe.Account.retrieve(page.stripe_account_id)

                external_account = {
                    "object": "bank_account",
                    "country": "US",
                    "account_number": form.cleaned_data['account_number'],
                    "account_holder_name": "%s %s" % (request.user.first_name, request.user.last_name),
                    "account_holder_type": stripe_type,
                    "routing_number": form.cleaned_data['routing_number'],
                    "default_for_currency": "true",
                }
                ext_acct = acct.external_accounts.create(external_account=external_account)
                # delete the old account here
                # so that we can set the new one as default first
                acct.external_accounts.retrieve(page.stripe_bank_account_id).delete()
                page.stripe_bank_account_id = ext_acct.id
            page.save()
            utils.email(request.user.email, "blank", "blank", "page_bank_information_updated")
#            return HttpResponseRedirect(page.get_absolute_url())
            return redirect('page_dashboard_admin', page_slug=page.page_slug)


@login_required
def page_edit(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    if utils.has_dashboard_access(request.user, page, 'manager_edit'):
        form = forms.PageForm(instance=page)
        if request.method == 'POST':
            form = forms.PageForm(instance=page, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'page/page_edit.html', {'page': page, 'form': form})

@login_required
def page_delete(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    if utils.has_dashboard_access(request.user, page, 'manager_delete'):
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
        new_subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe"}
    elif action == "unsubscribe":
        page.subscribers.remove(request.user.userprofile)
        new_subscribe_attr = {"name": "subscribe", "value": "Subscribe"}
    else:
        print("something went wrong")
    previous_page = request.META.get('HTTP_REFERER')
    expected_url = "/accounts/login/?next=/page/subscribe/"
    if expected_url in previous_page:
        return HttpResponseRedirect(page.get_absolute_url())
    else:
        new_subscribe_attr = json.dumps(new_subscribe_attr)
        return HttpResponse(new_subscribe_attr)

@login_required
def page_invite(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    if utils.has_dashboard_access(request.user, page, 'manager_invite'):
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
#                    utils.email(form.cleaned_data["email"], "", "", "new_page_created")
                    return redirect('page_dashboard_admin', page_slug=page.page_slug)
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
    if request.user.userprofile in page.admins.all() or manager == request.user:
        # remove the manager
        page.managers.remove(manager.userprofile)
        # revoke the permissions
        remove_perm('manager_edit', manager, page)
        remove_perm('manager_delete', manager, page)
        remove_perm('manager_invite', manager, page)
        remove_perm('manager_image_edit', manager, page)
        remove_perm('manager_view_dashboard', manager, page)
        # redirect to page admin
        return redirect('page_dashboard_admin', page_slug=page.page_slug)
    else:
        raise Http404

class PageDonate(View):
    def get(self, request, page_slug):
        template_params = {}
        page = get_object_or_404(Page, page_slug=page_slug)

        if request.user.is_authenticated():
            form = DonateForm()
            try:
                cards = get_user_credit_cards(request.user.userprofile)
                template_params["cards"] = cards
            except Exception as e:
                template_params["stripe_error"] = True
                error = {
                    "e": e,
                    "user": request.user.pk,
                    "page": page.pk,
                    "campaign": None,
                }
                error_email(error)
        else:
            form = DonateUnauthenticatedForm()

        template_params["page"] = page
        template_params["form"] = form
        template_params["api_pk"] = config.settings['stripe_api_pk']

        return render(self.request, 'page/page_donate.html', template_params)

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)

        if request.user.is_authenticated():
            form = DonateForm(request.POST)
        else:
            form = DonateUnauthenticatedForm(request.POST)
        if form.is_valid():
            donate(request=request, form=form, page=page, campaign=None)
            return HttpResponseRedirect(page.get_absolute_url())

@login_required
def page_image_delete(request, image_pk):
    image = get_object_or_404(PageImage, pk=image_pk)
    if utils.has_dashboard_access(request.user, image.page, 'manager_image_edit'):
        image.delete()
        return HttpResponse('')
    else:
        raise Http404

@login_required
def page_profile_update(request, image_pk):
    image = get_object_or_404(PageImage, pk=image_pk)
    if utils.has_dashboard_access(request.user, image.page, 'manager_image_edit'):
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

class PageAjaxDonations(View):
    def post(self, request):
        page = get_object_or_404(Page, pk=request.POST.get("page_pk"))
        sort_by = request.POST.get("sort_by")
        column = request.POST.get("column")
        column = column.split("sort-")[1]
        donationset = Donation.objects.filter(page=page)
        data = OrderedDict()
        for d in donationset:
            d.date = d.date.replace(tzinfo=timezone.utc).astimezone(tz=None)
            data["pk{}".format(d.pk)] = {
                "date": d.date.strftime("%b. %-d, %Y, %-I:%M %p"),
                "anonymous_amount": d.anonymous_amount,
                "anonymous_donor": d.anonymous_donor,
                "user": {
                    "first_name": d.donor_first_name,
                    "last_name": d.donor_last_name,
                },
            }
            if d.anonymous_amount is True:
               data["pk{}".format(d.pk)]["amount"] = 0
            else:
                data["pk{}".format(d.pk)]["amount"] = d.amount
            if d.anonymous_donor is True:
                data["pk{}".format(d.pk)]["user"]["first_name"] = ""
                data["pk{}".format(d.pk)]["user"]["last_name"] = ""
            if d.campaign:
                data["pk{}".format(d.pk)]["campaign"] = d.campaign.name
            else:
                data["pk{}".format(d.pk)]["campaign"] = ""
        if sort_by == "asc":
            if column == "donor_first_name":
                data = sorted(data.values(), key=lambda x: (x['user']['first_name'].lower()), reverse=True)
            else:
                data = sorted(data.values(), key=operator.itemgetter('{}'.format(column)), reverse=True)
        else:
            if column == "donor_first_name":
                data = sorted(data.values(), key=lambda x: (x['user']['first_name']).lower())
            else:
                data = sorted(data.values(), key=operator.itemgetter('{}'.format(column)))
        return HttpResponse(json.dumps(data), content_type="application/json")

class PageDashboard(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        if utils.has_dashboard_access(request.user, page, None):
            graph = donation_graph(page, 30)
            graph_dates = []
            graph_donations = []
            for k, v in graph.items():
                graph_dates.append(k.strftime('%b %-d'))
                graph_donations.append(int(v/100))
            graph_dates = list(reversed(graph_dates))
            graph_donations = list(reversed(graph_donations))
            return render(self.request, 'page/dashboard.html', {
                'page': page,
                'donations': donation_statistics(page),
                'graph_dates': graph_dates,
                'graph_donations': graph_donations,
            })
        else:
            raise Http404

class PageDashboardAdmin(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        invitations = ManagerInvitation.objects.filter(page=page, expired=False)
        if utils.has_dashboard_access(request.user, page, None):
            return render(self.request, 'page/dashboard_admin.html', {
                'page': page,
                'invitations': invitations,
            })
        else:
            raise Http404

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        print(request.POST.getlist('permissions[]'))
        utils.update_manager_permissions(request.POST.getlist('permissions[]'), page)
        return redirect('page_dashboard_admin', page_slug=page.page_slug)

class PageDashboardDonations(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        if utils.has_dashboard_access(request.user, page, None):
            return render(self.request, 'page/dashboard_donations.html', {
                'page': page,
                'donations': donation_statistics(page),
            })
        else:
            raise Http404

class PageDashboardCampaigns(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        if utils.has_dashboard_access(request.user, page, None):
            return render(self.request, 'page/dashboard_campaigns.html', {
                'page': page,
                'donations': donation_statistics(page),
                'campaign_types': campaign_types(page),
                'campaign_average_duration': campaign_average_duration(page),
                'campaign_success_pct': campaign_success_pct(page),
            })
        else:
            raise Http404

class PageDashboardImages(View):
    def get(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        if utils.has_dashboard_access(request.user, page, 'manager_image_edit'):
            images = PageImage.objects.filter(page=page)
            return render(self.request, 'page/dashboard_images.html', {
                'page': page,
                'images': images,
            })
        else:
            raise Http404

    def post(self, request, page_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        if utils.has_dashboard_access(request.user, page, 'manager_image_edit'):
            form = forms.PageImageForm(self.request.POST, self.request.FILES)
            data = image_is_valid(request, form, page)
            return JsonResponse(data)
        else:
            raise Http404

