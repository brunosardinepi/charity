from decimal import Decimal, ROUND_HALF_UP

import stripe

from .models import Donation
from pagefund import config
from userprofile.models import StripeCard


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

def unique_donor_check(request, page=None, campaign=None):
    page_donations = Donation.objects.filter(page=page, user=request.user)
    if campaign is None:
        if page_donations:
            return False
        else:
            return "page"
    else:
        campaign_donations = Donation.objects.filter(campaign=campaign, user=request.user)
        if page_donations:
            if campaign_donations:
                return False
            else:
                return "campaign"
        else:
            if campaign_donations:
                return False
            else:
                return "both"

def card_check(request, id):
    try:
        card = StripeCard.objects.get(user=request.user.userprofile, id=id)
        return card
    except StripeCard.DoesNotExist:
        print("not your card")
        return False

def charge_source(c, page=None, campaign=None):
    if page is not None:
        charge = stripe.Charge.create(
            amount=c["amount"],
            currency="usd",
            customer=c["customer_id"],
            source=c["card_source"],
            description="$%s donation to %s." % (c["form_amount"], page.name),
            receipt_email=c["user_email"],
            destination={
                "amount": c["final_amount"],
                "account": page.stripe_account_id,
            }
        )
    elif campaign is not None:
        charge = stripe.Charge.create(
            amount=c["amount"],
            currency="usd",
            customer=c["customer_id"],
            source=c["card_source"],
            description="$%s donation to %s via the %s campaign." % (c["form_amount"], campaign.page.name, campaign.name),
            receipt_email=c["user_email"],
            destination={
                "amount": c["final_amount"],
                "account": campaign.page.stripe_account_id,
            }
        )
    return charge

def donate(request, form, page=None, campaign=None):
    amount = form.cleaned_data['amount'] * 100
    stripe_fee = Decimal(amount * 0.029) + 30
    pagefund_fee = Decimal(amount * config.settings['pagefund_fee'])
    if form.cleaned_data['cover_fees'] == True:
        pagefund_fee += stripe_fee
    final_amount = amount - stripe_fee - pagefund_fee
    cents = Decimal('0')
    final_amount = final_amount.quantize(cents, ROUND_HALF_UP)

    if request.user.is_authenticated:
        saved_card = request.POST.get('saved_card')
        customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)
        c = {
            "amount": amount,
            "customer_id": customer.id,
            "form_amount": form.cleaned_data["amount"],
            "user_email": request.user.email,
            "final_amount": final_amount
        }
        if saved_card:
            try:
                saved_card = int(saved_card)
            except ValueError:
                print("not an int, possible tampering")
            card_source = card_check(request, saved_card)
            if card_source is not False:
                c["card_source"] = card_source.stripe_card_id
            charge = charge_source(c, page, campaign)
        elif request.POST.get('save_card'):
            customer, card_source = get_card_source(request)
            if card_source is None:
                card = create_card(request, customer)
                c["card_source"] = card.stripe_card_id
            if page is not None:
                charge = charge_source(c, page, None)
            elif campaign is not None:
                charge = charge_source(c, None, campaign)
        else:
            if page is not None:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=request.POST.get('stripeToken'),
                    description="$%s donation to %s." % (form.cleaned_data['amount'], page.name),
                    receipt_email=request.user.email,
                    destination={
                        "amount": final_amount,
                        "account": page.stripe_account_id,
                    }
                )
            elif campaign is not None:
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
    if page is None:
        page = campaign.page
        campaign.donation_money += amount
    page.donation_money += amount
    unique_donor = unique_donor_check(request=request, page=page, campaign=campaign)
    if unique_donor == "page":
        page.donation_count += 1
    elif unique_donor == "campaign":
        campaign.donation_count += 1
    elif unique_donor == "both":
        page.donation_count += 1
        campaign.donation_count += 1
    if campaign is not None:
        campaign.save()
    page.save()
    Donation.objects.create(
        amount=amount,
        anonymous_amount=form.cleaned_data['anonymous_amount'],
        anonymous_donor=form.cleaned_data['anonymous_donor'],
        comment=form.cleaned_data['comment'],
        page=page,
        campaign=campaign,
        stripe_charge_id=charge.id,
        user=request.user
     )

#def create_plan(request, amount):
    # create a plan in app
    # create a plan in stripe
