import stripe

from . import models

def create_plan(request, form, amount, page):
    customer = stripe.Customer.retrieve("%s" % request.user.userprofile.stripe_customer_id)

    # create the plan id
    plan_id = 'user-{}-page-{}'.format(request.user.pk, page.pk)

    # check if there's an existing plan
    # and delete it
    # then delete the subscription
    try:
        existing_plan = stripe.Plan.retrieve(plan_id)
        existing_plan.delete()
        plan_obj = models.StripePlan.objects.get(stripe_plan_id=plan_id)
        subscription = stripe.Subscription.retrieve(plan_obj.stripe_subscription_id)
        plan_obj.delete()
        subscription.delete()

    except stripe.error.InvalidRequestError as e:
        error = str(e)
        if 'No such plan' in error:
            # checked with stripe, there is no existing plan
            pass

    plan = stripe.Plan.create(
        product={
            "name": "Monthly ${} from {} {} to the '{}' Page.".format(
                int(amount / 100),
                request.user.first_name,
                request.user.last_name,
                page.name,
            ),
        },
        id=plan_id,
        interval="month",
        currency="usd",
        amount=amount,
        metadata={
            "page": page.pk,
            "pf_user_pk": request.user.pk,
            "anonymous_amount": form.cleaned_data['anonymous_amount'],
            "anonymous_donor": form.cleaned_data['anonymous_donor'],
            "comment": form.cleaned_data['comment'],
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
