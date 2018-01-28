import stripe

from . import models

def create_plan(request, form, amount, page=None, campaign=None):
    customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)
    if page is not None:
        plan = stripe.Plan.create(
            name="Monthly $%s from %s %s to the '%s' Page." % (amount, request.user.first_name, request.user.last_name, page.name),
            id="user-%s-page-%s" % (request.user.pk, page.pk),
            interval="month",
            currency="usd",
            amount=amount,
            metadata={
                "page": page.id,
                "pf_user_pk": request.user.pk,
                "anonymous_amount": form.cleaned_data['anonymous_amount'],
                "anonymous_donor": form.cleaned_data['anonymous_donor'],
                "comment": form.cleaned_data['comment']
            }
        )
    elif campaign is not None:
        plan = stripe.Plan.create(
            name="Monthly $%s from %s %s to the '%s' Campaign." % (amount, request.user.first_name, request.user.last_name, campaign.name),
            id="user-%s-campaign-%s" % (request.user.pk, campaign.pk),
            interval="month",
            currency="usd",
            amount=amount,
            metadata={
                "pf_user_pk": request.user.pk,
                "anonymous_amount": form.cleaned_data['anonymous_amount'],
                "anonymous_donor": form.cleaned_data['anonymous_donor'],
                "comment": form.cleaned_data['comment'],
                "campaign": campaign.id,
                "page": campaign.page.id
            }
        )
    subscription = stripe.Subscription.create(
        customer=customer,
        billing="charge_automatically",
        items=[
            {
                "plan": plan.id,
            },
        ],
    )

def delete_stripe_plan(stripe_plan_id):
    plan = stripe.Plan.retrieve(stripe_plan_id)
    plan.delete()

def delete_stripe_subscription(stripe_subscription_id):
    subscription = stripe.Subscription.retrieve(stripe_subscription_id)
    subscription.delete()
