from collections import OrderedDict
import json
import operator

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.contrib import messages
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
from notes.utils import error_email
from invitations.models import ManagerInvitation
from invitations.utils import invite
from page.models import Page
from pagefund import config, utils
from pagefund.image import image_is_valid
from pagefund.utils import email, has_notification
from userprofile import models as UserProfileModels
from userprofile.utils import get_user_credit_cards


def campaign(request, page_slug, campaign_pk, campaign_slug):
    try:
        campaign = Campaign.objects.get(pk=campaign_pk)
    except Campaign.DoesNotExist:
        return redirect('notes:error_campaign_does_not_exist')

    if campaign.deleted == False:
        template_params = {}

        if request.user.is_authenticated():
            template_params["form"] = CommentForm

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
        template_params["donate_form"] = donate_form
        template_params["api_pk"] = config.settings['stripe_api_pk']
        template_params["subscribe_attr"] = subscribe_attr
        return render(request, 'campaign/campaign.html', template_params)
    else:
        return redirect('notes:error_campaign_does_not_exist')

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

                substitutions = {
                    "-campaignname-": campaign.name,
                }
                email(request.user.email, "blank", "blank", "new_campaign_created", substitutions)

                date = timezone.now().strftime("%Y-%m-%d %I:%M:%S %Z")
                utils.email("gn9012@gmail.com", "blank", "blank", "admin_new_campaign", {
                    '-user-': request.user.email,
                    '-page-': campaign.page.name,
                    '-campaign-': campaign.name,
                    '-date-': date,
                })

                substitutions = {
                    "-campaignname-": campaign.name,
                    "-pagename-": campaign.page.name,
                    "-campaignurl-": "{}/{}/{}/{}/".format(config.settings['site'], campaign.page.page_slug, campaign.pk, campaign.campaign_slug),
                }
                admins = page.admins.all()
                for admin in admins:
                    if has_notification(admin.user, "notification_email_campaign_created") == True:
                        if admin.user != request.user:
                            email(admin.user.email, "blank", "blank", "new_campaign_created_admin", substitutions)
                managers = page.managers.all()
                for manager in managers:
                    if has_notification(manager.user, "notification_email_campaign_created") == True:
                        if manager.user != request.user:
                            email(manager.user.email, "blank", "blank", "new_campaign_created_admin", substitutions)

                if campaign.type == 'vote':
                    return redirect('campaign_edit_vote', page_slug=page.page_slug, campaign_pk=campaign.pk, campaign_slug=campaign.campaign_slug)
                else:
                    return HttpResponseRedirect(campaign.get_absolute_url())
        return render(request, 'campaign/campaign_create.html', {'form': form})


class CampaignEditVote(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if campaign.type == "vote":
            formset = forms.VoteParticipantInlineFormSet(
                queryset=campaign.voteparticipant_set.all(),
            )
            return render(request, 'campaign/campaign_edit_vote.html', {
                'campaign': campaign,
                'formset': formset,
            })
        else:
            raise Http404

    def post(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if campaign.type == "vote":
            formset = forms.VoteParticipantInlineFormSet(
                request.POST,
                request.FILES,
                queryset=campaign.voteparticipant_set.all(),
            )
            if formset.is_valid():
                vote_participants = formset.save(commit=False)
                for vote_participant in vote_participants:
                    vote_participant.campaign = campaign
                    vote_participant.save()
                for d in formset.deleted_objects:
                    d.delete()
                messages.success(request, 'Campaign updated', fail_silently=True)
                return redirect('campaign_dashboard_admin',
                    page_slug=campaign.page.page_slug,
                    campaign_pk=campaign.pk,
                    campaign_slug=campaign.campaign_slug
                )
            else:
                return redirect('notes:error_campaign_vote_participants')
        else:
            raise Http404

def create_search_result_html(r):
    html = (
        "<div class='row mb-4'>"
        "<div class='col-md-10 offset-md-2'>"
        "<div class='form-check'>"
        "<input class='form-check-input' type='radio' name='page' value='{}' id='page{}'>"
        "<label class='form-check-label' for='page{}'>"
        "<a class='pr-3' href='/{}/' target='_blank'>{}</a>"
        "</label>"
        "</div>"
        "</div>"
        "</div>"
    ).format(r.pk, r.pk, r.pk, r.page_slug, r.name)

    return html

def campaign_search_pages(request):
    if request.method == "POST":
        q = request.POST.get('q')

        if q == "0":
            q = False

        query = SearchQuery(q)
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        rank_metric = 0.2
        results = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, deleted=False).order_by('-rank')

        response_data = []
        if results:
            for r in results:
                response_data.append(create_search_result_html(r))

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

@login_required
def campaign_edit(request, page_slug, campaign_pk, campaign_slug):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if utils.has_dashboard_access(request.user, campaign, 'manager_edit'):
        form = forms.CampaignEditForm(instance=campaign)
        if request.method == 'POST':
            form = forms.CampaignEditForm(instance=campaign, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Campaign updated', fail_silently=True)
                return redirect('campaign_dashboard_admin',
                    page_slug=campaign.page.page_slug,
                    campaign_pk=campaign.pk,
                    campaign_slug=campaign.campaign_slug
                )
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

        messages.success(request, 'Campaign deleted', fail_silently=True)
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
                    messages.success(request, 'Invitation sent', fail_silently=True)
                    # redirect the admin/manager to the Campaign
                    return redirect('campaign_dashboard_admin',
                        page_slug=campaign.page.page_slug,
                        campaign_pk=campaign.pk,
                        campaign_slug=campaign.campaign_slug
                    )
        return render(request, 'campaign/campaign_invite.html', {'form': form, 'campaign': campaign})
    # the user isn't an admin or a manager, so they can't invite someone
    # the only way someone got here was by typing the url manually
    else:
        raise Http404

@login_required
def remove_manager(request, page_slug, campaign_pk, campaign_slug, manager_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    manager = get_object_or_404(User, pk=manager_pk)
    if request.user.userprofile in campaign.campaign_admins.all() or manager == request.user:
#    if utils.has_dashboard_access(request.user, campaign, None):
        # remove the manager
        campaign.campaign_managers.remove(manager.userprofile)
        # revoke the permissions
        remove_perm('manager_edit', manager, campaign)
        remove_perm('manager_delete', manager, campaign)
        remove_perm('manager_invite', manager, campaign)
        remove_perm('manager_image_edit', manager, campaign)
        remove_perm('manager_view_dashboard', manager, campaign)

        messages.success(request, 'Manager removed', fail_silently=True)
        # redirect to campaign
        return HttpResponseRedirect(campaign.get_absolute_url())
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
                form = BaseDonate()
            else:
                form = DonateUnauthenticatedForm()
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
            template_params["form"] = form
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
            messages.success(request, 'Donation successful', fail_silently=True)
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
    previous_page = request.META.get('HTTP_REFERER')
    expected_url = "/accounts/login/?next=/campaign/subscribe/"
    if expected_url in previous_page:
        return HttpResponseRedirect(campaign.get_absolute_url())
    else:
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
            graph = donation_graph(campaign, 30)
            graph_dates = []
            graph_donations = []
            for k, v in graph.items():
                graph_dates.append(k.strftime('%b %-d'))
                graph_donations.append(int(v/100))
            graph_dates = list(reversed(graph_dates))
            graph_donations = list(reversed(graph_donations))
            return render(self.request, 'campaign/dashboard.html', {
                'campaign': campaign,
                'donations': donation_statistics(campaign),
                'graph_dates': graph_dates,
                'graph_donations': graph_donations,
            })
        else:
            raise Http404

class CampaignDashboardAdmin(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        invitations = ManagerInvitation.objects.filter(campaign=campaign, expired=False)
        if utils.has_dashboard_access(request.user, campaign, None):
            return render(self.request, 'campaign/dashboard_admin.html', {
                'campaign': campaign,
                'invitations': invitations,
            })
        else:
            raise Http404

    def post(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        utils.update_manager_permissions(request.POST.getlist('permissions[]'), campaign)
        messages.success(request, 'Permissions updated', fail_silently=True)
        return redirect('campaign_dashboard_admin',
            page_slug=campaign.page.page_slug,
            campaign_pk=campaign.pk,
            campaign_slug=campaign.campaign_slug
        )

class CampaignDashboardDonations(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if utils.has_dashboard_access(request.user, campaign, 'manager_view_dashboard'):
            return render(self.request, 'campaign/dashboard_donations.html', {
                'campaign': campaign,
                'donations': donation_statistics(campaign),
            })
        else:
            raise Http404

class CampaignDashboardImages(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if utils.has_dashboard_access(request.user, campaign, 'manager_image_edit'):
            images = CampaignImage.objects.filter(campaign=campaign)
            return render(self.request, 'campaign/dashboard_images.html', {'campaign': campaign, 'images': images })
        else:
            raise Http404

    def post(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        if utils.has_dashboard_access(request.user, campaign, 'manager_image_edit'):
            form = forms.CampaignImageForm(self.request.POST, self.request.FILES)
            data = image_is_valid(request, form, campaign)
            if data:
                return JsonResponse(data)
            else:
                return HttpResponse('')
        else:
            raise Http404

class CampaignDonations(View):
    def get(self, request, page_slug, campaign_pk, campaign_slug):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        donations = Donation.objects.filter(campaign=campaign).order_by('-date')
        return render(self.request, 'campaign/campaign_donations_all.html', {
            'campaign': campaign,
            'donations': donations,
        })

