import json

from django.http import HttpResponse

from .utils import set_default_card
from userprofile.models import StripeCard


def default_card(request):
    if request.method == "POST":
        id = request.POST.get('id')
        id = id.split("-")[1]
        new_default = set_default_card(request, id)
        response_data = {
            'id': new_default.pk
        }
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
