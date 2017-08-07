from django.db.models.functions import Lower
from django.shortcuts import render

from collections import OrderedDict

from page import models as PageModels


def search(request):
    categories = OrderedDict(PageModels.Page._meta.get_field('category').choices)
    return render(request, 'search/search.html', {'categories': categories})

def results(request):
    if request.is_ajax():
        q = request.GET.get('q')
        if q:
            results = PageModels.Page.objects.filter(name__unaccent__trigram_similar=q).order_by('name')
            return render(request, 'search/results.html', {'results': results})
