from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View

from guardian.shortcuts import assign_perm, get_user_perms, remove_perm
import stripe

from . import forms
from .models import Campaign, CampaignImage
from .utils import email_new_campaign
from comments.forms import CommentForm
from donation.forms import DonateForm
from donation.models import Donation
from donation.utils import donate
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
        donate_form = DonateForm()
        template_params = {}

        if request.user.is_authenticated:
            cards = get_user_credit_cards(request.user.userprofile)
            template_params["cards"] = cards

        if request.method == "POST":
            utils.update_manager_permissions(request.POST.getlist('permissions[]'), campaign)

        template_params["campaign"] = campaign
        template_params["form"] = form
        template_params["donate_form"] = donate_form
        template_params["api_pk"] = config.settings['stripe_api_pk']
        return render(request, 'campaign/campaign.html', template_params)

@login_required
def campaign_create(request, page_slug):
    page = get_object_or_404(Page, page_slug=page_slug)
    form = forms.CampaignForm()
    if request.method == 'POST':
        form = forms.CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.page = page
            campaign.save()
            campaign.campaign_admins.add(request.user.userprofile)

            admins = page.admins.all()
            for admin in admins:
                email_new_campaign(admin.user.email, campaign)
            managers = page.managers.all()
            for manager in managers:
                email_new_campaign(manager.user.email, campaign)

            return HttpResponseRedirect(campaign.get_absolute_url())
    return render(request, 'campaign/campaign_create.html', {'form': form, 'page': page})

@login_required
def campaign_edit(request, page_slug, campaign_pk, campaign_slug):
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(Campaign, pk=campaign_pk)

    # write custom decorator for admin/manager check
    admin = request.user.userprofile in campaign.campaign_admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_edit', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
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
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(Campaign, pk=campaign_pk)

    # write custom decorator for admin/manager check
    admin = request.user.userprofile in campaign.campaign_admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_delete', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
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
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(Campaign, pk=campaign_pk)

    # write custom decorator for admin/manager check
    # True if the user is an admin
    admin = request.user.userprofile in campaign.campaign_admins.all()
    # True if the user is a manager and has the 'invite' permission
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_invite', campaign):
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
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    manager = get_object_or_404(User, pk=manager_pk)
    # only campaign admins can remove managers
    if request.user.userprofile in campaign.campaign_admins.all():
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
        admin = request.user.userprofile in campaign.page.admins.all()
        if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', campaign):
            manager = True
        else:
            manager = False
        if admin or manager:
            images = CampaignImage.objects.filter(campaign=campaign)
            return render(self.request, 'campaign/images.html', {'campaign': campaign, 'images': images })
        else:
            raise Http404

    def post(self, request, page_slug, campaign_pk, campaign_slug):
        page = get_object_or_404(Page, page_slug=page_slug)
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        admin = request.user.userprofile in campaign.page.admins.all()
        if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', campaign):
            manager = True
        else:
            manager = False
        if admin or manager:
            form = forms.CampaignImageForm(self.request.POST, self.request.FILES)
            data = image_is_valid(request, form, campaign)
            return JsonResponse(data)
        else:
            raise Http404

@login_required
def campaign_image_delete(request, image_pk):
    image = get_object_or_404(CampaignImage, pk=image_pk)
    # write custom decorator for admin/manager check
    admin = request.user.userprofile in image.campaign.campaign_admins.all()
    if request.user.userprofile in image.campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', image.campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
        image.delete()
        return HttpResponse('')
    else:
        raise Http404

@login_required
def campaign_profile_update(request, image_pk):
    image = get_object_or_404(CampaignImage, pk=image_pk)
    # write custom decorator for admin/manager check
    admin = request.user.userprofile in image.campaign.campaign_admins.all()
    if request.user.userprofile in image.campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', image.campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
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

def campaign_donate(request, campaign_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    if request.method == "POST":
        form = DonateForm(request.POST)
        if form.is_valid():
            donate(request=request, form=form, page=None, campaign=campaign)
            return HttpResponseRedirect(campaign.get_absolute_url())
