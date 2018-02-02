import datetime
import json
import pytz

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from .models import Webhook
from campaign.models import Campaign, VoteParticipant
from donation.models import Donation
from page.models import Page
from plans.models import StripePlan


@require_POST
@csrf_exempt
def webhooks_all(request):
    event_json = json.loads(request.body.decode('utf-8'))
    Webhook.objects.create(
        event_id=event_json['id'],
        object=event_json['object'],
        created=event_json['created'],
        type=event_json['type'],
        event=event_json
    )
    return HttpResponse(status=200)

@require_POST
@csrf_exempt
def charge_succeeded(request):
    event_json = json.loads(request.body.decode('utf-8'))
    date = datetime.datetime.utcfromtimestamp(event_json['data']['object']['created']).replace(tzinfo=pytz.utc)
    tz = pytz.timezone('America/Chicago')
    date = date.astimezone(tz)

    if not event_json['data']['object']['metadata']:
        invoice = stripe.Invoice.retrieve(event_json['data']['object']['invoice'])
        subscription = stripe.Subscription.retrieve(invoice['subscription'])
        anonymous_amount = subscription['plan']['metadata']['anonymous_amount']
        anonymous_donor = subscription['plan']['metadata']['anonymous_donor']
        try:
            campaign_pk = subscription['plan']['metadata']['campaign']
            campaign = get_object_or_404(Campaign, pk=campaign_pk)
        except KeyError:
            campaign = None
        page_pk = subscription['plan']['metadata']['page']
        try:
            comment = subscription['plan']['metadata']['comment']
        except KeyError:
            comment = ''
        pf_user_pk = subscription['plan']['metadata']['pf_user_pk']
        vote_participant = None
    else:
        anonymous_amount = event_json['data']['object']['metadata']['anonymous_amount']
        anonymous_donor = event_json['data']['object']['metadata']['anonymous_donor']
        try:
            campaign_pk = event_json['data']['object']['metadata']['campaign']
            campaign = get_object_or_404(Campaign, pk=campaign_pk)
        except KeyError:
            campaign = None
        page_pk = event_json['data']['object']['metadata']['page']
        try:
            comment = event_json['data']['object']['metadata']['comment']
        except KeyError:
            comment = ''
        # get the user's pk if this was a donation from a logged-in user
        try:
            pf_user_pk = event_json['data']['object']['metadata']['pf_user_pk']
        # get the donor's first/last name if they weren't logged in when they donated
        except KeyError:
            pf_user_pk = None
            first_name = event_json['data']['object']['metadata']['first_name']
            last_name = event_json['data']['object']['metadata']['last_name']
        try:
            vote_participant_pk = event_json['data']['object']['metadata']['vote_participant']
            vote_participant = get_object_or_404(VoteParticipant, pk=vote_participant_pk)
        except KeyError:
            vote_participant = None

    amount = event_json['data']['object']['amount']
    page = get_object_or_404(Page, pk=page_pk)
    stripe_charge_id = event_json['data']['object']['id']
    # get the user object if this was a donation from a logged-in user
    if pf_user_pk is not None:
        user = get_object_or_404(User, pk=pf_user_pk)
        if vote_participant is not None:
            Donation.objects.create(
                amount=amount,
                anonymous_amount=anonymous_amount,
                anonymous_donor=anonymous_donor,
                comment=comment,
                date=date,
                page=page,
                campaign=campaign,
                campaign_participant=vote_participant,
                stripe_charge_id=stripe_charge_id,
                user=user,
             )
        else:
            Donation.objects.create(
                amount=amount,
                anonymous_amount=anonymous_amount,
                anonymous_donor=anonymous_donor,
                comment=comment,
                date=date,
                page=page,
                campaign=campaign,
                stripe_charge_id=stripe_charge_id,
                user=user,
             )
    else:
        if vote_participant is not None:
            Donation.objects.create(
                amount=amount,
                anonymous_amount=anonymous_amount,
                anonymous_donor=anonymous_donor,
                comment=comment,
                date=date,
                page=page,
                campaign=campaign,
                campaign_participant=vote_participant,
                stripe_charge_id=stripe_charge_id,
                donor_first_name=first_name,
                donor_last_name=last_name,
             )
        else:
            Donation.objects.create(
                amount=amount,
                anonymous_amount=anonymous_amount,
                anonymous_donor=anonymous_donor,
                comment=comment,
                date=date,
                page=page,
                campaign=campaign,
                stripe_charge_id=stripe_charge_id,
                donor_first_name=first_name,
                donor_last_name=last_name,
             )

    return HttpResponse(status=200)

@require_POST
@csrf_exempt
def customer_subscription_created(request):
    event_json = json.loads(request.body.decode('utf-8'))

    amount = event_json['data']['object']['plan']['amount']
    page_pk = event_json['data']['object']['plan']['metadata']['page']
    page = get_object_or_404(Page, pk=page_pk)
    try:
        campaign_pk = event_json['data']['object']['plan']['metadata']['campaign']
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
    except KeyError:
        campaign = None
    interval = event_json['data']['object']['plan']['interval']
    pf_user_pk = event_json['data']['object']['plan']['metadata']['pf_user_pk']
    user = get_object_or_404(User, pk=pf_user_pk)
    plan = event_json['data']['object']['plan']['id']
    subscription = event_json['data']['object']['id']

    StripePlan.objects.create(
        user=user,
        amount=amount,
        page=page,
        campaign=campaign,
        interval=interval,
        stripe_plan_id=plan,
        stripe_subscription_id=subscription,
    )

    return HttpResponse(status=200)

@require_POST
@csrf_exempt
def customer_subscription_deleted(request):
    event_json = json.loads(request.body.decode('utf-8'))

    subscription_id = event_json['data']['object']['id']
    plan = get_object_or_404(StripePlan, stripe_subscription_id=subscription_id)
    plan.delete()

    return HttpResponse(status=200)
