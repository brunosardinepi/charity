from collections import OrderedDict
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render
from functools import reduce
from itertools import chain

import json
import operator

from .utils import query_list
from campaign.models import Campaign
from donation.templatetags.donation_extras import cents_to_dollars
from page.models import Page


def search(request):
    if request.method == "POST":
        query_from_search = request.POST.get('q')
    else:
        query_from_search = None
    categories = OrderedDict(Page._meta.get_field('category').choices)

    return render(request, 'search/search.html', {
        'categories': categories,
        'query_from_search': query_from_search,
    })

def create_search_result_html(r, sponsored, trending):
    html = (
        "<div class='row mb-4'>"
        "<div class='col-md-auto search-result-picture-container'>"
    )

    if r.profile_picture():
        src = r.profile_picture().image.url
        height = r.profile_picture().height
        width = r.profile_picture().width
        if height < (width - 60):
            html += "<div class='circular-landscape-sm'>"
        elif height > (width + 60):
            html += "<div class='circular-portrait-sm'>"
        else:
            html += "<div class='circular-square-sm'>"
    else:
        html += "<div class='circular-square'>"
        src = "/static/img/campaign_default.svg"

    if isinstance(r, Page):
        html += "<img src='{}' />".format(src)
    elif isinstance(r, Campaign):
        html += "<img src='{}' />".format(src)

    html += (
        "</div>"
        "</div>"
        "<div class='col-md-10 mb-4'>"
        "<div class='row justify-content-between'>"
        "<div class='col-md-auto'>"
    )

    if isinstance(r, Page):
        html += "<h3><a class='purple' href='/{}/'>{}</a></h3>".format(r.page_slug, r.name)
    elif isinstance(r, Campaign):
        html += "<h3><a class='teal' href='/{}/{}/{}/'>{}</a></h3>".format(r.page.page_slug, r.pk, r.campaign_slug, r.name)

    html += (
        "</div>"
        "<div class='trending col-md-auto mr-auto d-flex align-items-center h100'>"
    )

    if sponsored == True:
        html += "<i class='fal fa-star mr-3' aria-hidden title='Sponsored'></i><span class='sr-only'>Sponsored</span>"

    if trending == True:
        html += "<i class='fal fa-chart-line mr-3' aria-hidden title='Trending'></i><span class='sr-only'>Trending</span>"

    html += (
        "</div>"
        "<div class='col-md-auto vote-amount'>"
    )

    if isinstance(r, Page):
        html += "<span class='purple font-weight-bold font-size-175'>{}</span>".format(cents_to_dollars(r.donation_money()))
    elif isinstance(r, Campaign):
        html += "<span class='teal font-weight-bold font-size-175'>{}</span>".format(cents_to_dollars(r.donation_money()))

    html += (
        "</div>"
        "</div>"
        "<span class='comment-content'><p>{}</p></span>"
        "</div>"
        "</div>"
    ).format(r.search_description())

    return html

def results(request):
    if request.method == "POST":
        q = request.POST.get('q')

        if q == "0":
            q = False

        if q:
            results, sponsored = query_list(q)
        else:
            results = None
            sponsored = None

        trending_pages = Page.objects.filter(deleted=False, stripe_verified=True).order_by('-trending_score')[:10]
        trending_campaigns = Campaign.objects.filter(deleted=False, is_active=True).order_by('-trending_score')[:10]

        response_data = []
        if sponsored:
            for s in sponsored:
                if s in trending_pages or s in trending_campaigns:
                    response_data.append(create_search_result_html(s, True, True))
                else:
                    response_data.append(create_search_result_html(s, True, False))

        if results:
            for r in results:
                if r in trending_pages or r in trending_campaigns:
                    response_data.append(create_search_result_html(r, False, True))
                else:
                    response_data.append(create_search_result_html(r, False, False))

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
