import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import StripePlan
from .utils import delete_stripe_plan, delete_stripe_subscription

def delete_plan(request):
    if request.method == "POST":
        id = request.POST.get('id')
        id = id.split("-")[1]

        plan = get_object_or_404(StripePlan, id=id)

        delete_stripe_plan(plan.stripe_plan_id)
        delete_stripe_subscription(plan.stripe_subscription_id)

        return HttpResponse('')
