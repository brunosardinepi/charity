from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from guardian.shortcuts import assign_perm, get_user_perms, remove_perm
import stripe

from . import forms
from . import models
from comments.forms import CommentForm
from comments.models import Comment
from donation.models import Donation
from invitations.models import ManagerInvitation
from page.forms import PageDonateForm
from page.models import Page
from pagefund import config, utils
from pagefund.email import email
from userprofile import models as UserProfileModels


def campaign(request, page_slug, campaign_pk, campaign_slug):
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)
    if campaign.deleted == True:
        raise Http404
    else:
        form = CommentForm
        donate_form = PageDonateForm()

        if request.method == "POST":
            utils.update_manager_permissions(request.POST.getlist('permissions[]'), campaign)

        return render(request, 'campaign/campaign.html', {
            'campaign': campaign,
            'form': form,
            'donate_form': donate_form,
            'api_pk': config.settings['stripe_api_pk'],
        })

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

            subject = "Campaign created!"
            body = "You just created a Campaign called '%s' for the '%s' Page." % (
                campaign.name,
                page.name
            )
            email(request.user.email, subject, body)

            body = "A Campaign called '%s' has just been created by %s for the '%s' Page." % (
                campaign.name,
                request.user.email,
                page.name
            )
            admins = page.admins.all()
            for admin in admins:
                email(admin.user.email, subject, body)
            managers = page.managers.all()
            for manager in managers:
                email(manager.user.email, subject, body)

            return HttpResponseRedirect(campaign.get_absolute_url())
    return render(request, 'campaign/campaign_create.html', {'form': form, 'page': page})

@login_required
def campaign_edit(request, page_slug, campaign_pk, campaign_slug):
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)

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
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)

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
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)

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
                # check if the person we are inviting is already a manager
                try:
                    user = User.objects.get(email=form.cleaned_data['email'])
                    if user.userprofile in campaign.campaign_managers.all():
                        return HttpResponseRedirect(campaign.get_absolute_url())
                except User.DoesNotExist:
                    print("no user found")

                # check if the user has already been invited by this admin/manager for this campaign
                # expired should be False, otherwise the previous invitation has expired and we are OK with them getting a new one
                # accepted/declined are irrelevant if the invite has expired, so we don't check these
                try:
                    invitation = ManagerInvitation.objects.get(
                        invite_to=form.cleaned_data['email'],
                        invite_from=request.user,
                        campaign=campaign,
                        expired=False
                    )
                except ManagerInvitation.DoesNotExist:
                    invitation = None

                # if this user has already been invited, redirect the admin/manager
                # need to notify the admin/manager that the person has already been invited
                if invitation:
                    # this user has already been invited, so do nothing
                    return HttpResponseRedirect(campaign.get_absolute_url())
                # if the user hasn't been invited already, create the invite and send it to them
                else:
                    # create the invitation object and set the permissions
                    invitation = ManagerInvitation.objects.create(
                        invite_to=form.cleaned_data['email'],
                        invite_from=request.user,
                        campaign=campaign,
                        manager_edit=form.cleaned_data['manager_edit'],
                        manager_delete=form.cleaned_data['manager_delete'],
                        manager_invite=form.cleaned_data['manager_invite'],
                        manager_image_edit=form.cleaned_data['manager_image_edit'],
                    )

                    # create the email
                    subject = "Campaign invitation!"
                    body = "%s %s has invited you to become an admin of the '%s' campaign. <a href='%s/invite/manager/accept/%s/%s/'>Click here to accept.</a> <a href='%s/invite/manager/decline/%s/%s/'>Click here to decline.</a>" % (
                        request.user.first_name,
                        request.user.last_name,
                        campaign.name,
                        config.settings['site'],
                        invitation.pk,
                        invitation.key,
                        config.settings['site'],
                        invitation.pk,
                        invitation.key
                    )
                    email(form.cleaned_data['email'], subject, body)
                    # redirect the admin/manager to the campaign
                    return HttpResponseRedirect(campaign.get_absolute_url())
        return render(request, 'campaign/campaign_invite.html', {'form': form, 'campaign': campaign})
    # the user isn't an admin or a manager, so they can't invite someone
    # the only way someone got here was by typing the url manually
    else:
        raise Http404

@login_required
def remove_manager(request, page_slug, campaign_pk, campaign_slug, manager_pk):
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)
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
        # redirect to campaign
        return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404

@login_required
def campaign_image_upload(request, page_slug, campaign_pk, campaign_slug):
#    page = get_object_or_404(Page, page_slug=page_slug)
#    campaign = get_object_or_404(models.Campaign, pk=campaign_pk, campaign_slug=campaign_slug, page=page)
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)

    # write custom decorator for admin/manager check
    admin = request.user.userprofile in campaign.page.admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
        form = forms.CampaignImagesForm(instance=campaign)
        if request.method == 'POST':
            form = forms.CampaignImagesForm(data=request.POST, files=request.FILES)
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
                imageupload.campaign=campaign
                try:
                    profile = models.CampaignImages.objects.get(campaign=imageupload.campaign, campaign_profile=True)
                except models.CampaignImages.DoesNotExist:
                    profile = None
                if profile and imageupload.campaign_profile:
                    profile.campaign_profile=False
                    profile.save()
                imageupload.campaign=campaign
                imageupload.save()
            return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404
    return render(request, 'campaign/campaign_image_upload.html', {'campaign': campaign, 'form': form })

@login_required
def campaign_image_delete(request, page_slug, campaign_slug, campaign_pk, image_pk):
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)
    image = get_object_or_404(models.CampaignImages, pk=image_pk)

    # write custom decorator for admin/manager check
    admin = request.user.userprofile in campaing.campaign_admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
        image.delete()
        return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404

@login_required
def campaign_profile_update(request, page_slug, campaign_slug, campaign_pk, image_pk):
#    page = get_object_or_404(Page, page_slug=page_slug)
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)
    image = get_object_or_404(models.CampaignImages, pk=image_pk)

    # write custom decorator for admin/manager check
    admin = request.user.userprofile in campaign.campaign_admins.all()
    if request.user.userprofile in campaign.campaign_managers.all() and request.user.has_perm('manager_image_edit', campaign):
        manager = True
    else:
        manager = False
    if admin or manager:
        try:
            profile = models.CampaignImages.objects.get(campaign=image.campaign, campaign_profile=True)
        except models.CampaignImages.DoesNotExist:
            profile = None
        if profile:
            profile.campaign_profile = False
            profile.save()
            image.campaign_profile = True
            image.save()
        else:
            image.campaign_profile = True
            image.save()
        return HttpResponseRedirect(campaign.get_absolute_url())
    else:
        raise Http404

def campaign_donate(request, campaign_pk):
    campaign = get_object_or_404(models.Campaign, pk=campaign_pk)
    if request.method == "POST":
        form = PageDonateForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount'] * 100
#            stripe_fee = int(amount * 0.029) + 30
#            pagefund_fee = int(amount * config.settings['pagefund_fee'])
#            final_amount = amount - stripe_fee - pagefund_fee
            final_amount = utils.donation_amount(amount)
            if form.cleaned_data['save_card'] == True:
                if request.user.is_authenticated:
                    customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)

                    customer_cards = request.user.userprofile.stripecard_set.all()
#                    print("customer_cards = %s" % customer_cards)
                    card_check = stripe.Token.retrieve(request.POST.get('stripeToken'))
#                    print("card_check fingerprint = %s" % card_check['card']['fingerprint'])
                    customer_card_dict = {}
                    if customer_cards:
#                        print("there are customer_cards")
                        for c in customer_cards:
                            if c.stripe_card_fingerprint == card_check['card']['fingerprint']:
                                card_source = c.stripe_card_id
#                                print("existing card_source = %s" % card_source)
                                break
                            else:
                                card_source = None
                    else:
                        card_source = None

                    if card_source is None:
#                        print("card_source is None")
                        card_source = customer.sources.create(source=request.POST.get('stripeToken'))
#                        print("card_source = %s" % card_source.id)
#                        print("card_source_fingerprint = %s" % card_source.fingerprint)
                        UserProfileModels.StripeCard.objects.create(
                            user=request.user.userprofile,
                            stripe_card_id=card_source.id,
                            stripe_card_fingerprint=card_source.fingerprint
                        )

                    charge = stripe.Charge.create(
                        amount=amount,
                        currency="usd",
                        customer=customer.id,
                        source=card_source,
                        description="$%s donation to %s via the %s campaign." % (form.cleaned_data['amount'], campaign.page.name, campaign.name),
                        receipt_email=request.user.email,
                        destination={
                            "amount": final_amount,
                            "account": campaign.page.stripe_account_id,
                        }
                    )
            else:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=request.POST.get('stripeToken'),
                    description="$%s donation to %s via the %s campaign." % (form.cleaned_data['amount'], campaign.page.name, campaign.name),
                    receipt_email=request.user.email,
                    destination={
                        "amount": final_amount,
                        "account": campaign.page.stripe_account_id,
                    }
                )

            Donation.objects.create(
                amount=amount,
                anonymous=form.cleaned_data['anonymous'],
                comment=form.cleaned_data['comment'],
                page=campaign.page,
                campaign=campaign,
                stripe_charge_id=charge.id,
                user=request.user
            )
 #           print("donation = %s" % float(amount / 100))
 #           print("stripe takes = %s" % float(stripe_fee / 100))
 #           print("we keep = %s" % float(pagefund_fee / 100))
 #           print("charity gets = %s" % float(final_amount / 100))
            return HttpResponseRedirect(campaign.get_absolute_url())
