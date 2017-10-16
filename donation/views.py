import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from userprofile.models import StripeCard


def default_card(request):
    if request.method == "POST":
        id = request.POST.get('id')
        id = id.split("-")[1]
        # find the current default
        try:
            default = StripeCard.objects.get(user=request.user.userprofile, default=True)
        except StripeCard.DoesNotExist:
            print("no default")
            default = None
        except StripeCard.MultipleObjectsReturned:
            print("multiple default cards found, bad")
        # if there is a current default, remove the default tag
        if default:
            default.default = False
            default.save()
        # set the new card as the default
        new_default = get_object_or_404(StripeCard, id=id)
        new_default.default = True
        new_default.save()

        response_data = {
            'id': new_default.pk
        }
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
