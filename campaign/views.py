from collections import OrderedDict
import json
import operator

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from guardian.shortcuts import assign_perm, get_user_perms, remove_perm
import stripe

from . import forms
from .models import Campaign, CampaignImage, VoteParticipant
from .utils import email_new_campaign
from comments.forms import CommentForm
from donation.forms import BaseDonate, DonateForm, DonateUnauthenticatedForm
from donation.models import Donation
from donation.utils import donate, donation_graph, donation_statistics
from error.utils import error_email
from invitations.models import ManagerInvitation
from invitations.utils import invite
from page.models import Page
from pagefund import config, utils
from userprofile import models as UserProfileModels
from userprofile.utils import get_user_credit_cards
from pagefund.image import image_is_valid


def campaign(request, page_slug, campaign_pk, campaign_slug):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if campaign.deleted == True:
        raise Http404
    else:
        form = CommentForm
        template_params = {}

        if not campaign.type == "vote":
            donate_form = BaseDonate()
            if request.user.is_authenticated:
                try:
                    cards = get_user_credit_cards(request.user.userprofile)
                    template_params["cards"] = cards
                except Exception as e:
                    template_params["stripe_error"] = True
                    error = {
                        "e": e,
                        "user": request.user.pk,
                        "page": campaign.page.pk,
                        "campaign": campaign.pk,
                    }
                    error_email(error)
            else:
                user_subscription_check = None
        else:
            donate_form = None

        try:
            user_subscription_check = campaign.campaign_subscribers.get(user_id=request.user.pk)
        except UserProfileModels.UserProfile.DoesNotExist:
            user_subscription_check = None

        if user_subscription_check:
            subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
        else:
            subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}

        if request.method == "POST":
            utils.update_manager_permissions(request.POST.getlist('permissions[]'), campaign)

        template_params["campaign"] = campaign
        template_params["form"] = form
        template_params["donate_form"] = donate_form
        template_params["api_pk"] = config.settings['stripe_api_pk']
        template_params["subscribe_attr"] = subscribe_attr
        return render(request, 'campaign/campaign.html', template_params)


class CampaignCreate(View):
    def get(self, request, page_slug=None):
        data = {}
        if page_slug is not None:
            page = get_object_or_404(Page, page_slug=page_slug)
            data['page'] = page
        form = forms.CampaignForm()
        data['form'] = form
        return render(request, 'campaign/campaign_create.html', data)
    def post(self, request):
        form = forms.CampaignForm(request.POST)
        if form.is_valid():
            # check if the user selected a page and redirect to a an error page if needed
            page_pk = request.POST.get('page')
            if page_pk:
                page = get_object_or_404(Page, pk=page_pk)
                campaign = form.save(commit=False)
                campaign.user = request.user
                campaign.page = page
                campaign.save()
                campaign.campaign_admins.add(request.user.userprofile)
                campaign.campaign_subscribers.add(request.user.userprofile)

                admins = page.admins.all()
                for admin in admins:
                    email_new_campaign(admin.user.email, campaign)
                managers = page.managers.all()
                for manager in managers:
                    email_new_campaign(manager.user.email, campaign)

                if campaign.type == 'vote':
                    return redirect('campaign_create_vote', campaign_pk=campaign.pk)
                else:
                    return HttpResponseRedirect(campaign.get_absolute_url())
            else:
                # redirect to error page
                print("no page selected")


class CampaignCreateVote(View):
    def get(self, request, campaign_pk):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        print("get, campaign = {}".format(campaign))
        print("campaign name = {}, pk = {}".format(campaign.name, campaign.pk))
        formset = forms.VoteParticipantInlineFormSet(
            queryset=VoteParticipant.objects.none(),
        )
        return render(request, 'campaign/campaign_create_vote.html', {
            'campaign': campaign,
            'formset': formset,
        })
    def post(self, request, campaign_pk):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        print("post, campaign = {}".format(campaign))
        formset = forms.VoteParticipantInlineFormSet(request.POST)
        if formset.is_valid():
            formset.save(commit=False)
            for f in formset:
                if f.is_valid() and not f.empty_permitted:
                    vote_participant = f.save(commit=False)
                    vote_participant.campaign = campaign
                    vote_participant.save()
            return HttpResponseRedirect(campaign.get_absolute_url())

class CampaignEditVote(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        q = VoteParticipant.objects.filter(campaign=campaign)
        formset = forms.VoteParticipantInlineFormSet(queryset=q)
        return render(request, 'campaign/campaign_edit_vote.html', {
            'campaign': campaign,
            'formset': formset,
        })
    def post(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        print("post, campaign = {}".format(campaign))
        formset = forms.VoteParticipantInlineFormSet(request.POST)
        if formset.is_valid():
            formset.save(commit=False)
            for f in formset:
                if f.is_valid() and not f.empty_permitted:
                    vote_participant = f.save(commit=False)
                    vote_participant.campaign = campaign
                    vote_participant.save()
            for d in formset.deleted_objects:
                d.delete()
            return HttpResponseRedirect(campaign.get_absolute_url())
        else:
            print("invalid")

def campaign_search_pages(request):
    if request.method == "POST":
        q = request.POST.get('q')

        if q == "0":
            q = False

        query = SearchQuery(q)
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        rank_metric = 0.2
        results = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=False, deleted=False).order_by('-rank')

        response_data = OrderedDict()
        if results:
            for r in results:
                response_data[r.page_slug] = {
                    'pk': r.pk,
                    'name': r.name,
                    'city': r.city,
                    'state': r.state,
                }
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

@login_required
def campaign_edit(request, page_slug, campaign_pk, campaign_slug):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if utils.has_dashboard_access(request.user, campaign, 'manager_edit'):
        form = forms.CampaignForm(instance=campaign)
        if request.method == 'POST':
            form = forms.CampaignForm(instance=campaign, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_edit.html', {'campaign': campaign, 'form': form})

@login_required
def campaign_delete(request, page_slug, campaign_pk, campaign_slug):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if utils.has_dashboard_access(request.user, campaign, 'manager_delete'):
        campaign.deleted = True
        campaign.deleted_by = request.user
        campaign.deleted_on = timezone.now()
        campaign.name = campaign.name + "_deleted_" + timezone.now().strftime("%Y%m%d")
        campaign.campaign_slug = campaign.campaign_slug + "deleted" + timezone.now().strftime("%Y%m%d")
        campaign.save()
        return HttpResponseRedirect(campaign.page.get_absolute_url())
    else:
        raise Http404

@login_required
def campaign_invite(request, page_slug, campaign_pk, campaign_slug):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if utils.has_dashboard_access(request.user, campaign, 'manager_invite'):
        form = forms.ManagerInviteForm()
        if request.method == 'POST':
            form = forms.ManagerInviteForm(request.POST)
            if form.is_valid():
                data = {
                    "request": request,
                    "form": form,
                    "page": None,
                    "campaign": campaign
                }

                status = invite(data)
                if status == True:
                    # redirect the admin/manager to the Campaign
                    return HttpResponseRedirect(campaign.get_absolute_url())
        return render(request, 'campaign/campaign_invite.html', {'form': form, 'campaign': campaign})
    # the user isn't an admin or a manager, so they can't invite someone
    # the only way someone got here was by typing the url manually
    else:
        raise Http404

@login_required
def remove_manager(request, page_slug, campaign_pk, campaign_slug, manager_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    manager = get_object_or_404(User, pk=manager_pk)
    if utils.has_dashboard_access(request.user, campaign, None):
        # remove the manager
        campaign.campaign_managers.remove(manager.userprofile)
        # revoke the permissions
        remove_perm('manager_edit', manager, campaign)
        remove_perm('manager_delete', manager, campaign)
        remove_perm('manager_invite', manager, campaign)
        remove_perm('manager_image_edit', manager, campaign)
        remove_perm('manager_view_dashboard', manager, campaign)
        # redirect to campaign
        return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404

class CampaignImageUpload(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if utils.has_dashboard_access(request.user, campaign, 'manager_image_edit'):
            images = CampaignImage.objects.filter(campaign=campaign)
            return render(self.request, 'campaign/images.html', {'campaign': campaign, 'images': images })
        else:
            raise Http404

    def post(self, request, page_slug, campaign_pk, campaign_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if utils.has_dashboard_access(request.user, campaign, 'manager_image_edit'):
            form = forms.CampaignImageForm(self.request.POST, self.request.FILES)
            data = image_is_valid(request, form, campaign)
            return JsonResponse(data)
        else:
            raise Http404

@login_required
def campaign_image_delete(request, image_pk):
    image = get_object_or_404(CampaignImage, pk=image_pk)
    if utils.has_dashboard_access(request.user, image.campaign, 'manager_image_edit'):
        image.delete()
        return HttpResponse('')
    else:
        raise Http404

@login_required
def campaign_profile_update(request, image_pk):
    image = get_object_or_404(CampaignImage, pk=image_pk)
    if utils.has_dashboard_access(request.user, image.campaign, 'manager_image_edit'):
        try:
            profile_picture = CampaignImage.objects.get(campaign=image.campaign, profile_picture=True)
        except CampaignImage.DoesNotExist:
            profile_picture = None
        if profile_picture:
            profile_picture.profile_picture = False
            profile_picture.save()
        image.profile_picture = True
        image.save()
        return HttpResponse('')
    else:
        raise Http404


class CampaignDonate(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug, vote_participant_pk=None):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if vote_participant_pk is not None:
            vote_participant = get_object_or_404(VoteParticipant, pk=vote_participant_pk)
        else:
            vote_participant = None
        if campaign.deleted == True:
            raise Http404
        else:
            if request.user.is_authenticated():
                donate_form = BaseDonate()
            else:
                donate_form = DonateUnauthenticatedForm()
            template_params = {}

            if request.user.is_authenticated:
                try:
                    cards = get_user_credit_cards(request.user.userprofile)
                    template_params["cards"] = cards
                except Exception as e:
                    template_params["stripe_error"] = True
                    error = {
                        "e": e,
                        "user": request.user.pk,
                        "page": campaign.page.pk,
                        "campaign": campaign.pk,
                    }
                    error_email(error)
            template_params["campaign"] = campaign
            template_params["donate_form"] = donate_form
            template_params["api_pk"] = config.settings['stripe_api_pk']
            template_params["vote_participant"] = vote_participant
            return render(request, 'campaign/donate.html', template_params)

    def post(self, request, page_slug, campaign_pk, campaign_slug, vote_participant_pk=None):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if request.user.is_authenticated():
            form = BaseDonate(request.POST)
        else:
            form = DonateUnauthenticatedForm(request.POST)
        if form.is_valid():
            donate(request=request, form=form, page=None, campaign=campaign)
            return HttpResponseRedirect(campaign.get_absolute_url())

@login_required
def subscribe(request, campaign_pk, action=None):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if action == "subscribe":
        campaign.campaign_subscribers.add(request.user.userprofile)
        new_subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
    elif action == "unsubscribe":
        campaign.campaign_subscribers.remove(request.user.userprofile)
        new_subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}
    else:
        print("something went wrong")
    new_subscribe_attr = json.dumps(new_subscribe_attr)
    return HttpResponse(new_subscribe_attr)

class CampaignAjaxDonations(View):
    def post(self, request):
        campaign = get_object_or_404(Campaign, pk=request.POST.get("campaign_pk"))
        sort_by = request.POST.get("sort_by")
        column = request.POST.get("column")
        column = column.split("sort-")[1]
        donationset = Donation.objects.filter(campaign=campaign)
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
            data["pk{}".format(d.pk)]["campaign"] = d.campaign.name
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


class CampaignDashboard(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if utils.has_dashboard_access(request.user, campaign, None):
            return render(self.request, 'campaign/dashboard.html', {
                'campaign': campaign,
                'donations': donation_statistics(campaign),
                'graph': donation_graph(campaign, 30),
            })
        else:
            raise Http404

    def post(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        utils.update_manager_permissions(request.POST.getlist('permissions[]'), campaign)
        return redirect('campaign_dashboard', page_slug=campaign.page.page_slug, campaign_pk=campaign.pk, campaign_slug=campaign.campaign_slug)
