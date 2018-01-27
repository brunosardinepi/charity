from django.shortcuts import get_object_or_404, redirect

from .models import StripePlan
from .utils import delete_stripe_plan, delete_stripe_subscription


def delete_plan(request, plan_pk):
    plan = get_object_or_404(StripePlan, pk=plan_pk)
    delete_stripe_plan(plan.stripe_plan_id)
    delete_stripe_subscription(plan.stripe_subscription_id)

    return redirect('userprofile:userprofile')
