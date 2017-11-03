from collections import OrderedDict

from django.db.models import F, Sum

from campaign.models import Campaign
from campaign.utils import campaign_duration
from donation.models import Donation


def campaign_types(page):
    choices = Campaign._meta.get_field('type').flatchoices
    choices = {key: value for (key, value) in choices}
    campaign_types = OrderedDict()
    for c,v in choices.items():
        campaigns = Campaign.objects.filter(page=page, type=c, is_active=True, deleted=False)
        c_sum = 0
        for campaign in campaigns:
            campaign_sum = Donation.objects.filter(page=page, campaign=campaign).aggregate(Sum('amount')).get('amount__sum')
            if campaign_sum is None:
                campaign_sum = 0
            c_sum += campaign_sum
        campaign_types[c] = {
            'count': campaigns.count(),
            'sum': c_sum,
            'display': v
        }
    return campaign_types

def campaign_average_duration(page):
    campaigns = Campaign.objects.filter(page=page, is_active=False, deleted=False, donation_money__gte=F('goal'))
    durations = []
    for c in campaigns:
        durations.append(campaign_duration(c))
    if len(durations) > 0:
        return sum(durations) / len(durations)
    else:
        return 0
