import stripe

from . import models

def create_plan(request, amount, page=None, campaign=None):
    customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)
    if page is not None:
        stripe_plan = models.StripePlan.objects.create(
            user=request.user,
            amount=amount * 100,
            page=page,
            interval="monthly",
        )
        plan = stripe.Plan.create(
            name="Monthly $%s from %s %s to the '%s' Page." % (amount, request.user.first_name, request.user.last_name, page.name),
            id=stripe_plan.pk,
            interval="month",
            currency="usd",
            amount=amount * 100,
        )
    elif campaign is not None:
        stripe_plan = models.StripePlan.objects.create(
            user=request.user,
            amount=amount * 100,
            campaign=campaign,
        )
        plan = stripe.Plan.create(
            name="Monthly $%s from %s %s to the '%s' Campaign." % (amount, request.user.first_name, request.user.last_name, campaign.name),
            id=stripe_plan.pk,
            interval="month",
            currency="usd",
            amount=amount * 100,
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
    print(subscription)
