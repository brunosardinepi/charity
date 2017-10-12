import stripe

from .models import Donation
from pagefund import config
from userprofile.models import StripeCard


def create_card(request, customer):
    card_source = customer.sources.create(source=request.POST.get('stripeToken'))
    StripeCard.objects.create(
        user=request.user.userprofile,
        stripe_card_id=card_source.id,
        stripe_card_fingerprint=card_source.fingerprint
    )

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

def donate(request, form, page=None, campaign=None):
    amount = form.cleaned_data['amount'] * 100
    stripe_fee = int(amount * 0.029) + 30
    pagefund_fee = int(amount * config.settings['pagefund_fee'])
    if form.cleaned_data['cover_fees'] == True:
        pagefund_fee += stripe_fee
    final_amount = amount - stripe_fee - pagefund_fee

    if form.cleaned_data['saved_card'] == True:
        print(form.cleaned_data['saved_card'])
    elif form.cleaned_data['save_card'] == True:
        if request.user.is_authenticated:
            customer, card_source = get_card_source(request)
            if card_source is None:
                create_card(request, customer)
            if page is not None:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    customer=customer.id,
                    source=card_source,
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
