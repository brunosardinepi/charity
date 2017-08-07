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
        f = request.GET.get('f')

        if q == "0":
            q = False
        elif f == "0":
            f = False

        if all([q, f]):
            print("q and f")
        if q:
            results = PageModels.Page.objects.filter(name__unaccent__trigram_similar=q).order_by('name')
            return render(request, 'search/results.html', {'results': results})
        if f:
            f = f.split(",")
            results = []
            for i in f:
                query_objects = PageModels.Page.objects.filter(category=i).order_by('name')
                if query_objects:
                    for object in query_objects:
                        results.append(object)
            return render(request, 'search/results.html', {'results': results})
