from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from functools import reduce
from itertools import chain

import operator

from campaign.models import Campaign
from page.models import Page


def filter_list(f, s=''):
    f = f.split(",")
    results = []
    sponsored = []
    for i in f:
        if s:
            query_page = Page.objects.filter(category=i, state=s, deleted=False).order_by('name')
        else:
            query_page = Page.objects.filter(category=i, deleted=False).order_by('name')
        if query_page:
            for object in query_page:
                if object.is_sponsored == True:
                    sponsored.append(object)
                else:
                    results.append(object)
                campaigns = Campaign.objects.filter(page=object, deleted=False, is_active=True).order_by('name')
                for c in campaigns:
                    if c.page.is_sponsored == True:
                        sponsored.append(c)
                    else:
                        results.append(c)
    results.sort(key=lambda x: x.name.lower())
    sponsored.sort(key=lambda x: x.name.lower())
    return (results, sponsored)

def query_list(q, s=''):
    q = q.split(",")
    queries = [SearchQuery(query) for query in q]
    query = reduce(operator.or_, queries)
    vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
    rank_metric = 0.2
    if s:
        results_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=False, state=s, deleted=False).order_by('-rank')
        sponsored_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=True, state=s, deleted=False).order_by('-rank')
        results_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=False, state=s, deleted=False).order_by('-rank')
        sponsored_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=True, state=s, deleted=False).order_by('-rank')
    else:
        results_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=False, deleted=False).order_by('-rank')
        sponsored_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=True, deleted=False).order_by('-rank')
        results_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=False, deleted=False).order_by('-rank')
        sponsored_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=True, deleted=False).order_by('-rank')
    results = list(chain(results_page, results_campaign))
    sponsored = list(chain(sponsored_page, sponsored_campaign))
    results.sort(key=lambda x: x.rank, reverse=True)
    sponsored.sort(key=lambda x: x.rank, reverse=True)
    return (results, sponsored)

def state_list(s):
    results = Page.objects.filter(is_sponsored=False, state=s, deleted=False).order_by('name')
    sponsored = Page.objects.filter(is_sponsored=True, state=s, deleted=False).order_by('name')
    return (results, sponsored)
