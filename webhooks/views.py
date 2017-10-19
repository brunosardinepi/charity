import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@require_POST
@csrf_exempt
def charge_succeeded(request):
    print("accessed 'charged_succeeded")
    event_json = json.loads(request.body.decode('utf-8'))
#    print(event_json)
    print(json.dumps(event_json, indent=4, sort_keys=True))
#    print(type(request.body))
#    print(request.body)
    return HttpResponse(status=200)
