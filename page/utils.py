from collections import OrderedDict

from django.db.models import Sum

from campaign.models import Campaign
from campaign.utils import campaign_duration, campaign_reached_goal
from donation.models import Donation


def campaign_types(page):
    # get a list of tuples of campaign types
    choices = Campaign._meta.get_field('type').flatchoices
    # convert to a dictionary
    choices = {key: value for (key, value) in choices}
    # empty ordered dictionary
    # that will be used to store information about each campaign type
    campaign_types = OrderedDict()
    for c, v in choices.items():
        # find all of the campaigns that are of this type
        campaigns = Campaign.objects.filter(page=page, type=c, is_active=True, deleted=False)
        c_sum = 0
        for campaign in campaigns:
            # campaign_sum = total amount of donations for this campaign
            campaign_sum = Donation.objects.filter(page=page, campaign=campaign).aggregate(Sum('amount')).get('amount__sum')
            if campaign_sum is None:
                campaign_sum = 0
            # add this campaign's donation sum
            # to this campaign type's total donation amount
            c_sum += campaign_sum
        # create a dictionary entry for this campaign type that has
        # the number of campaigns of this type,
        # the total donation amount for campaigns of this type,
        # and the display name for this type
        campaign_types[c] = {
            'count': campaigns.count(),
            'sum': c_sum,
            'display': v
        }
    return campaign_types

def campaign_average_duration(page):
    # find all campaigns for this page that have ended
    campaigns = Campaign.objects.filter(page=page, is_active=False, deleted=False)
    print("campaigns = {}".format(campaigns))
    durations = []
    for c in campaigns:
        # find how much money the campaign raised
#        donation_money = c.donation_money()
        # check if the campaign met its goal
#        if donation_money is not None and donation_money > c.goal:
            # find this campaign's duration
#            durations.append(campaign_duration(c))
        durations.append(campaign_duration(c))
        print("duration = {}".format(campaign_duration(c)))
    # find the average duration
    if len(durations) > 0:
        return int(sum(durations) / len(durations))
    else:
        return 0

def campaign_success_pct(page):
    # find the campaign types
    types = campaign_types(page)
    # empty ordered dictionary to store information about campaign success pct
    success = OrderedDict()
    for c, v in types.items():
        # get all of the campaigns that are this type
        campaigns = Campaign.objects.filter(page=page, type=c, is_active=False, deleted=False)
        c_goals = []
        for campaign in campaigns:
            # check if each campaign reached its goal
            goal = campaign_reached_goal(campaign)
            if goal is True:
                # tally mark for success
                c_goals.append(1)
            elif goal is False:
                # tally mark for failure
                c_goals.append(0)
        # if there were campaigns, find the success pct
        if len(c_goals) > 0:
            # success_pct = success tally marks / total tally marks
            success_pct = sum(c_goals) / len(c_goals)
        # otherwise, 0% success rate
        else:
            success_pct = 0
        # add an entry to the dictionary for the campaign type that has
        # the campaign type display name,
        # the campaign type success pct
        success[c] = {
            'display': v["display"],
            'success_pct': success_pct
        }
    return success
