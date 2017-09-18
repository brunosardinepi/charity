from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render

from collections import OrderedDict
from functools import reduce
from itertools import chain

import json
import operator

from campaign.models import Campaign
from page.models import Page


def search(request):
    categories = OrderedDict(Page._meta.get_field('category').choices)
    states = OrderedDict(Page._meta.get_field('state').choices)
    return render(request, 'search/search.html', {'categories': categories, 'states': states})

def filter_list(f, s=''):
    f = f.split(",")
    results = []
    sponsored = []
    for i in f:
        if s:
            query_page = Page.objects.filter(category=i, state=s).order_by('name')
        else:
            query_page = Page.objects.filter(category=i).order_by('name')
        if query_page:
            for object in query_page:
                if object.is_sponsored == True:
                    sponsored.append(object)
                else:
                    results.append(object)
                campaigns = Campaign.objects.filter(page=object).order_by('name')
                for c in campaigns:
                    if c.page.is_sponsored == True:
                        sponsored.append(c)
                    else:
                        results.append(c)
    return (results, sponsored)

def query_list(q, s=''):
    q = q.split(",")
    queries = [SearchQuery(query) for query in q]
    query = reduce(operator.or_, queries)
    vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
    rank_metric = 0.2
    if s:
        results_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=False, state=s).order_by('-rank')
        sponsored_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=True, state=s).order_by('-rank')
        results_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=False, state=s).order_by('-rank')
        sponsored_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=True, state=s).order_by('-rank')
    else:
        results_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=False).order_by('-rank')
        sponsored_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=True).order_by('-rank')
        results_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=False).order_by('-rank')
        sponsored_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=True).order_by('-rank')
    results = list(chain(results_page, results_campaign))
    sponsored = list(chain(sponsored_page, sponsored_campaign))
    return (results, sponsored)

def state_list(s):
    results = Page.objects.filter(is_sponsored=False, state=s).order_by('name')
    sponsored = Page.objects.filter(is_sponsored=True, state=s).order_by('name')
    return (results, sponsored)

def results(request):
    if request.method == "POST":
        q = request.POST.get('q')
        f = request.POST.get('f')
        s = request.POST.get('s')
        a = request.POST.get('a')

        if a == "false":
            if f:
                f = f.replace('"', '')
                f = f.replace('[', '')
                f = f.replace(']', '')

            if q == "0":
                q = False
            elif f == "0":
                f = False

            if all([q, f]):
                results = []
                sponsored = []
                pages, sponsored_pages = query_list(q, s)
                f = f.split(",")
                for x in f:
                    p = [n for n in pages if n.category == x]
                    for y in p:
                        results.append(y)
                    s = [t for t in sponsored_pages if t.category == x]
                    for y in s:
                        sponsored.append(y)
            elif q:
                results, sponsored = query_list(q, s)
            elif f:
                results, sponsored = filter_list(f, s)
            elif s:
                results, sponsored = state_list(s)
            else:
                results = None
                sponsored = None
        elif a == "pages":
            results = Page.objects.filter(is_sponsored=False).order_by('name')
            sponsored = Page.objects.filter(is_sponsored=True).order_by('name')
        elif a == "campaigns":
            results = Campaign.objects.filter(page__is_sponsored=False).order_by('name')
            sponsored = Campaign.objects.filter(page__is_sponsored=True).order_by('name')

        response_data = OrderedDict()
        if results:
            for r in results:
                if isinstance(r, Page):
                    response_data[r.page_slug] = {
                        'name': r.name,
                        'city': r.city,
                        'state': r.state,
                        'sponsored': 'f',
                        'model': 'page'
                    }
                elif isinstance(r, Campaign):
                    response_data[r.campaign_slug] = {
                        'name': r.name,
                        'city': r.city,
                        'state': r.state,
                        'sponsored': 'f',
                        'model': 'campaign',
                        'page_slug': r.page.page_slug,
                        'pk': r.pk
                    }
        if sponsored:
            for s in sponsored:
                if isinstance(s, Page):
                    response_data[s.page_slug] = {
                        'name': s.name,
                        'city': s.city,
                        'state': s.state,
                        'sponsored': 't',
                        'model': 'page'
                    }
                elif isinstance(s, Campaign):
                    response_data[s.campaign_slug] = {
                        'name': s.name,
                        'city': s.city,
                        'state': s.state,
                        'sponsored': 't',
                        'model': 'campaign',
                        'page_slug': s.page.page_slug,
                        'pk': s.pk
                    }

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
