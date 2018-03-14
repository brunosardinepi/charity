from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from functools import reduce
from itertools import chain

import operator

from campaign.models import Campaign
from page.models import Page


def query_list(q):
    q = q.split(",")
    queries = [SearchQuery(query) for query in q]
    query = reduce(operator.or_, queries)
    vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
    rank_metric = 0.2

    results_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=False, deleted=False).order_by('-rank')
    sponsored_page = Page.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, is_sponsored=True, deleted=False).order_by('-rank')
    results_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=False, deleted=False, is_active=True).order_by('-rank')
    sponsored_campaign = Campaign.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=rank_metric, page__is_sponsored=True, deleted=False, is_active=True).order_by('-rank')

    results = list(chain(results_page, results_campaign))
    sponsored = list(chain(sponsored_page, sponsored_campaign))
    results.sort(key=lambda x: x.rank, reverse=True)
    sponsored.sort(key=lambda x: x.rank, reverse=True)

    return (results, sponsored)
