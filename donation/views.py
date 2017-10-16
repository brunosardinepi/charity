from django.shortcuts import render


def default_card(request):
    if request.method == "POST":
        id = request.POST.get('id')
        print(id)
