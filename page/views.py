from django.shortcuts import get_object_or_404, render
from django.http import Http404

from . import models
from campaign import models as CampaignModels


def page(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    active_campaigns = CampaignModels.Campaign.objects.filter(is_active=True)
    inactive_campaigns = CampaignModels.Campaign.objects.filter(is_active=False)
    return render(request, 'page/page.html', {
                                            'page': page,
                                            'active_campaigns': active_campaigns,
                                            'inactive_campaigns': inactive_campaigns
                                            })

def page_edit(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    if request.user.userprofile in page.admins.all():
        return render(request, 'page/page_edit.html', {'page': page})
    else:
        raise Http404
