from django.db.models.functions import Lower
from django.shortcuts import render

from collections import OrderedDict

from page import models as PageModels


def search(request):
    categories = OrderedDict(PageModels.Page._meta.get_field('category').choices)
    return render(request, 'search/search.html', {'categories': categories})

def filter_list(f):
    f = f.split(",")
    results = []
    for i in f:
        query_objects = PageModels.Page.objects.filter(category=i).order_by('name')
        if query_objects:
            for object in query_objects:
                results.append(object)
    return results

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
            results = []
            pages = PageModels.Page.objects.filter(name__unaccent__trigram_similar=q)
            print("pages")
            print(pages)
#            for page in pages:
#                results.append(page)
#            print("results")
#            print(results)
#            f_list = filter_list(f)
#            print("f")
#            print(f)
#            print("f_list")
#            print(f_list)
#            for f in f_list:
#                print("f")
#                print(f)
#                r = pages.filter(category=f)
#                print("r")
#                print(r)
#                for i in r:
#                    results.append(i)
#            print("results")
#            print(results)
            f = f.split(",")
            print("f")
            print(f)
            for x in f:
                p = pages.filter(category=x)
                print("pages")
                print(pages)
                for y in p:
                    results.append(y)
#            results = pages
        elif q:
            print("q")
            results = PageModels.Page.objects.filter(name__unaccent__trigram_similar=q).order_by('name')
        elif f:
            print("f")
            results = filter_list(f)
        return render(request, 'search/results.html', {'results': results})
