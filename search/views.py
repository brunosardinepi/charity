from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.db.models.functions import Lower
from django.shortcuts import render

from collections import OrderedDict
from functools import reduce

import operator

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

def query_list(q):
    q = q.split(",")
    queries = [SearchQuery(query) for query in q]
    query = reduce(operator.or_, queries)
    vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
    results = PageModels.Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.2).order_by('-rank')
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
            results = []
            pages = query_list(q)
            f = f.split(",")
            for x in f:
                p = pages.filter(category=x)
                for y in p:
                    results.append(y)
        elif q:
            results = query_list(q)
        elif f:
            results = filter_list(f)
        else:
            results = None
        return render(request, 'search/results.html', {'results': results})
