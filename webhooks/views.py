import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from campaign.models import Campaign
from donation.models import Donation
from page.models import Page

@require_POST
@csrf_exempt
def charge_succeeded(request):
    event_json = json.loads(request.body.decode('utf-8'))
    print(json.dumps(event_json, indent=4, sort_keys=True))

    amount = event_json['data']['object']['amount']
    anonymous_amount = event_json['data']['object']['metadata']['anonymous_amount']
    anonymous_donor = event_json['data']['object']['metadata']['anonymous_donor']

    try:
        campaign = get_object_or_404(Campaign, pk=event_json['data']['object']['metadata']['campaign'])
    except:
        campaign = None
    page = get_object_or_404(Page, pk=event_json['data']['object']['metadata']['page'])
    try:
        comment = event_json['data']['object']['metadata']['comment']
    except:
        comment = ''
    stripe_charge_id = event_json['data']['object']['id']
    pf_user_pk = event_json['data']['object']['metadata']['pf_user_pk']
    user = get_object_or_404(User, pk=pf_user_pk)


    Donation.objects.create(
        amount=amount,
        anonymous_amount=anonymous_amount,
        anonymous_donor=anonymous_donor,
        comment=comment,
        page=page,
        campaign=campaign,
        stripe_charge_id=stripe_charge_id,
        user=user
     )

    print("donation created")
    return HttpResponse(status=200)
