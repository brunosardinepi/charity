from collections import OrderedDict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

import stripe

from .models import Donation
from campaign.models import Campaign
from page.models import Page
from pagefund.utils import email, has_notification
from pagefund import config
from plans.models import StripePlan
from plans.utils import create_plan
from userprofile.models import StripeCard


def set_default_card(request, id):
    # find the current default
    try:
        default = StripeCard.objects.get(user=request.user.userprofile, default=True)
    except StripeCard.DoesNotExist:
        default = None
    except StripeCard.MultipleObjectsReturned:
        # multiple default cards found, bad
        return None
    # if there is a current default, remove the default tag
    if default:
        default.default = False
        default.save()
    # set the new card as the default
    new_default = get_object_or_404(StripeCard, id=id)
    new_default.default = True
    new_default.save()
    # update stripe
    customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)
    customer.default_source = new_default.stripe_card_id
    customer.save()
    return new_default

def create_card(request, customer):
    card_source = customer.sources.create(source=request.POST.get('stripeToken'))
    card = StripeCard.objects.create(
        user=request.user.userprofile,
        stripe_card_id=card_source.id,
        stripe_card_fingerprint=card_source.fingerprint
    )

    return card

def get_card_source(request):
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
    return customer, card_source

def card_check(request, id):
    try:
        card = StripeCard.objects.get(user=request.user.userprofile, id=id)
        return card
    except StripeCard.DoesNotExist:
        # not your card
        return False

def charge_source(c, page=None, campaign=None):
    if page is not None:
        charge = stripe.Charge.create(
            amount=c['amount'],
            currency='usd',
            customer=c['customer_id'],
            source=c['card_source'],
            description='$%s donation to %s.' % (int(c['amount'] / 100), page.name),
            receipt_email=c['user_email'],
            destination={
                'amount': c['final_amount'],
                'account': page.stripe_account_id,
            },
            metadata={
                'anonymous_amount': c['anonymous_amount'],
                'anonymous_donor': c['anonymous_donor'],
                'comment': c['comment'],
                'page': page.id,
                'pf_user_pk': c['pf_user_pk']
            }
        )
    elif campaign is not None:
        metadata = {
            'anonymous_amount': c['anonymous_amount'],
            'anonymous_donor': c['anonymous_donor'],
            'comment': c['comment'],
            'campaign': campaign.id,
            'page': campaign.page.id,
            'pf_user_pk': c['pf_user_pk'],
        }
        try:
            metadata['vote_participant'] = c['vote_participant']
        except KeyError:
            pass
        charge = stripe.Charge.create(
                amount=c['amount'],
                currency='usd',
                customer=c['customer_id'],
                source=c['card_source'],
                description='$%s donation to %s via the %s campaign.' % (int(c['amount'] / 100), campaign.page.name, campaign.name),
                receipt_email=c['user_email'],
                destination={
                    'amount': c['final_amount'],
                    'account': campaign.page.stripe_account_id,
                },
                metadata=metadata,
            )
    return charge

def donate(request, form, page=None, campaign=None):
    amount = form.cleaned_data['amount']
    preset_amount = request.POST.get('preset-amount')
    if amount:
        amount *= 100
    elif preset_amount:
        amount = int(preset_amount) * 100
    stripe_fee = Decimal(amount * 0.029) + 30
    pagefund_fee = Decimal(amount * config.settings['pagefund_fee'])
    final_amount = amount - stripe_fee - pagefund_fee
    cents = Decimal('0')
    final_amount = final_amount.quantize(cents, ROUND_HALF_UP)

    metadata = {}
    metadata["anonymous_amount"] = form.cleaned_data['anonymous_amount']
    metadata["anonymous_donor"] = form.cleaned_data['anonymous_donor']
    metadata["comment"] = form.cleaned_data['comment']
    metadata["pf_user_pk"] = request.user.pk
    if request.POST.get('vote_participant'):
        metadata["vote_participant"] = request.POST.get('vote_participant')

    if request.user.is_authenticated:
        saved_card = request.POST.get('saved_card')
        customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)
        c = {
            "amount": amount,
            "customer_id": customer.id,
            "user_email": request.user.email,
            "final_amount": final_amount,
            "anonymous_amount": form.cleaned_data['anonymous_amount'],
            "anonymous_donor": form.cleaned_data['anonymous_donor'],
            "comment": form.cleaned_data['comment'],
            "pf_user_pk": request.user.pk,
        }
        if request.POST.get('vote_participant'):
            c["vote_participant"] = request.POST.get('vote_participant')
        if saved_card:
            try:
                saved_card = int(saved_card)
            except ValueError:
                # not an int, possible tampering
                saved_card = None
            card_source = card_check(request, saved_card)
            if card_source is not False:
                c["card_source"] = card_source.stripe_card_id
            # check if the user wants this to be a monthly payment
            if request.POST.get('monthly'):
                # set this saved card as the default card
                set_default_card(request, card_source.id)
                # create the plan and charge them
                create_plan(request, form, amount, page, campaign)
            else:
                # this is a one-time donation, charge the card
                charge = charge_source(c, page, campaign)
        elif request.POST.get('save_card'):
            customer, card_source = get_card_source(request)
            if card_source is None:
                card = create_card(request, customer)
                c["card_source"] = card.stripe_card_id
            # check if the user wants this to be a monthly payment
            if request.POST.get('monthly'):
                # set this saved card as the default card
                set_default_card(request, card.id)
                # create the plan and charge them
                create_plan(request, form, amount, page, campaign)
            else:
                # this is a one-time donation, charge the card
                charge = charge_source(c, page, campaign)
        else:
            if campaign is not None:
                metadata["campaign"] = campaign.id
                metadata["page"] = campaign.page.id

                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=request.POST.get('stripeToken'),
                    description="${} donation to {} via the {} campaign.".format(int(amount / 100), campaign.page.name, campaign.name),
                    destination={
                        "amount": final_amount,
                        "account": campaign.page.stripe_account_id,
                    },
                    metadata=metadata,
                )

            elif page is not None:
                metadata["page"] = page.id

                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=request.POST.get('stripeToken'),
                    description="${} donation to {}.".format(int(amount / 100), page.name),
                    destination={
                        "amount": final_amount,
                        "account": page.stripe_account_id,
                    },
                    metadata=metadata,
                )
    else:
        metadata["first_name"] = form.cleaned_data['first_name']
        metadata["last_name"] = form.cleaned_data['last_name']
        if campaign is not None:
            metadata["campaign"] = campaign.id
            metadata["page"] = campaign.page.id

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=request.POST.get('stripeToken'),
                description="${} donation to {} via the {} campaign.".format(int(amount / 100), campaign.page.name, campaign.name),
                destination={
                    "amount": final_amount,
                    "account": campaign.page.stripe_account_id,
                },
                metadata=metadata,
            )

        elif page is not None:
            metadata["page"] = page.id

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=request.POST.get('stripeToken'),
                description="${} donation to {}.".format(int(amount / 100), page.name),
                destination={
                    "amount": final_amount,
                    "account": page.stripe_account_id,
                },
                metadata=metadata,
            )

    if page is None:
        page = campaign.page
    if campaign is not None:
        campaign.save()
    page.save()

    substitutions = {
        "-amount-": "${}".format(int(amount / 100)),
    }

    if campaign:
        substitutions['-recipient-'] = campaign.name
    else:
        substitutions['-recipient-'] = page.name

    if has_notification(request.user, "notification_email_donation") == True:
        email(request.user.email, "blank", "blank", "donation", substitutions)

    date = timezone.now().strftime("%Y-%m-%d %I:%M:%S %Z")
    substitutions['-user-'] = request.user.email
    substitutions['-date-'] = date
    email("gn9012@gmail.com", "blank", "blank", "admin_new_donation", substitutions)

def donation_statistics(obj):
    if obj.__class__ is Page:
        total_donations = Donation.objects.filter(page=obj).aggregate(Sum('amount')).get('amount__sum')
        total_donations_count = Donation.objects.filter(page=obj).count()
        if total_donations_count > 0:
            total_donations_avg = total_donations / total_donations_count
        else:
            total_donations = 0
            total_donations_avg = 0

        page_donations = Donation.objects.filter(page=obj, campaign__isnull=True).aggregate(Sum('amount')).get('amount__sum')
        page_donations_count = Donation.objects.filter(page=obj, campaign__isnull=True).count()
        if page_donations_count > 0:
            page_donations_avg = page_donations / page_donations_count
        else:
            page_donations = 0
            page_donations_avg = 0

        campaign_donations = Donation.objects.filter(page=obj, campaign__isnull=False).aggregate(Sum('amount')).get('amount__sum')
        campaign_donations_count = Donation.objects.filter(page=obj, campaign__isnull=False).count()
        if campaign_donations_count > 0:
            campaign_donations_avg = campaign_donations / campaign_donations_count
        else:
            campaign_donations = 0
            campaign_donations_avg = 0

        plan_donations = StripePlan.objects.filter(page=obj, campaign__isnull=True).aggregate(Sum('amount')).get('amount__sum')
        plan_donations_count = StripePlan.objects.filter(page=obj, campaign__isnull=True).count()
        if plan_donations_count > 0:
            plan_donations_avg = plan_donations / plan_donations_count
        else:
            plan_donations = 0
            plan_donations_avg = 0
        donations = {
            'total_donations': total_donations,
            'total_donations_avg': total_donations_avg,
            'page_donations': page_donations,
            'page_donations_avg': page_donations_avg,
            'campaign_donations': campaign_donations,
            'campaign_donations_avg': campaign_donations_avg,
            'plan_donations': plan_donations,
            'plan_donations_avg': plan_donations_avg
        }
    elif obj.__class__ is Campaign:
        total_donations = Donation.objects.filter(campaign=obj).aggregate(Sum('amount')).get('amount__sum')
        total_donations_count = Donation.objects.filter(campaign=obj).count()
        if total_donations_count > 0:
            total_donations_avg = total_donations / total_donations_count
        else:
            total_donations = 0
            total_donations_avg = 0

        donations = {
            'total_donations': total_donations,
            'total_donations_avg': total_donations_avg,
        }
    return donations

def donation_graph(obj, days):
    today = date.today()
    graph = OrderedDict()
    # for each day between today and x days ago,
    # find the donations for that day and
    # average them, then
    # add a dictionary k,v pair for date,avg
    for d in (today - timedelta(n) for n in range(days)):
        if obj.__class__ is Page:
            donations_sum = Donation.objects.filter(page=obj, date__year=d.year, date__month=d.month, date__day=d.day).aggregate(Sum('amount')).get('amount__sum')
        elif obj.__class__ is Campaign:
            donations_sum = Donation.objects.filter(campaign=obj, date__year=d.year, date__month=d.month, date__day=d.day).aggregate(Sum('amount')).get('amount__sum')
        if donations_sum is None:
            donations_sum = 0
        graph[d] = donations_sum
    return graph

def donation_history(obj):
    if obj.__class__ is Page:
        history = Donation.objects.filter(page=obj)
    return history
