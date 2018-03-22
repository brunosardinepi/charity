#!/home/gnowak/pagefund/pagefundenv/bin/python3

from collections import Counter, OrderedDict
from decimal import Decimal
import config
import psycopg2
import statistics


def trim(l, p):
    # copy of the list
    x = list(l)
    # convert the percentage to a decimal
    p /= 100
    # length of the list
    c = len(x)
    # make sure there are at least 4 items in the list before trimming
    # anything less would leave us with too few results
    if c > 3:
        # find the top and bottom percentage number
        r = int(c * p)
        # make sure we have something to trim
        if r > 0:
            # sort the list
            x.sort()
            # delete the top and bottom percentage number
            del x[:r]
            del x[-r:]
    # return the trimmed list
    return x

def trimmed_mean(l, p):
    # trim the list
    x = trim(l, p)
    # return the mean of the trimmed list
    return int(statistics.mean(x))

def trimmed_stdev(l, p):
    # trim the list
    x = trim(l, p)
    # return the standard deviation of the trimmed list
    return int(statistics.pstdev(x))

def find_ties(cur):
    # sort by trending score from highest to lowest
    scores = []

    # get a list of the duplicate trending scores
    query = "select trending_score from campaign_campaign where deleted = 'f' and is_active = 't' order by trending_score desc;"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row)
        scores.append(row[0])
        print("*" * 20)
    print(scores)

    # find the duplicate scores in the list to determine ties
    scores = [c for c, count in Counter(scores).items() if count > 1]
    print(scores)
    # new dict to hold the ties
    campaigns = {}
    # for each trending score, get a list of the campaigns that have that trending score
    for score in scores:
        campaigns_list = []
        query = "select id from campaign_campaign where trending_score = {};".format(score)
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            campaigns_list.append(row[0])
        campaigns[score] = campaigns_list
    print(campaigns)

    return campaigns

def break_ties(cur, ties):
    # go through each key in the ties dictionary
    print(ties)
    for k in ties:
        # run the campaigns through the trending function, but divide the points by 10 to make them a decimal,
        print(k)
        trending(cur, ties[k], 10, 100, True)
    # and add them to the current trending score instead of replacing it

def trending(cur, campaign_ids, trim_pct, factor, breaking_ties=False):
    # find the content type for pages
    cur.execute("select id from django_content_type where model = 'campaign';")
    c = cur.fetchone()
    content_type_id = c[0]

    # find the comments, donation_count, and donation_amount for each campaign and put them in their own list
    # initialize the lists we need for storing data later
    comments, donation_count, donation_amount = [], [], []
    campaigns = {}
    # do for each campaign
    for p in campaign_ids:
        # find the number of comments for the campaign
        query = "select count(*) from comments_comment where object_id = '{}' and content_type_id = '{}' and deleted = 'f';".format(p, content_type_id)
        cur.execute(query)
        c = cur.fetchall()
        c = c[0][0]
        if c is None:
            c = 0
        # append to the comments list
        comments.append(c)
        print("c = %s" % c)

        # find the number of donations for the campaign
        query = "select count(*) from donation_donation where campaign_id = '%s';" % p
        cur.execute(query)
        dc = cur.fetchall()
        dc = dc[0][0]
        if dc is None:
            dc = 0
        # append to the donation list
        donation_count.append(dc)
        print("dc = %s" % dc)

        # find the total amount of the donations for the page
        query = "select sum(amount) from donation_donation where campaign_id = '%s';" % p
        cur.execute(query)
        da = cur.fetchall()
        da = da[0][0]
        if da is None:
            da = 0
        # append to the donation amount list
        donation_amount.append(da)
        print("da = %s" % da)

        # store in a dict for access later
        campaigns[p] = {
            'comments': c,
            'donation_count': dc,
            'donation_amount': da,
        }

        if breaking_ties is True:
            # get the existing trending score
            query = "select trending_score from campaign_campaign where id = '{}';".format(p)
            cur.execute(query)
            rows = cur.fetchall()
            campaigns[p]['points'] = rows[0][0]
        else:
            # reset the trending score
            campaigns[p]['points'] = 0

        print(campaigns[p]['points'])

    # once all the stats have been added to their own lists, find the trimmed mean and trimmed stdev for each stat
    c_avg, c_stdev = trimmed_mean(comments, trim_pct), trimmed_stdev(comments, trim_pct)
    print("c_avg = %s" % c_avg)
    print("c_stdev = %s" % c_stdev)
    dc_avg, dc_stdev = trimmed_mean(donation_count, trim_pct), trimmed_stdev(donation_count, trim_pct)
    print("dc_avg = %s" % dc_avg)
    print("dc_stdev = %s" % dc_stdev)
    da_avg, da_stdev = trimmed_mean(donation_amount, trim_pct), trimmed_stdev(donation_amount, trim_pct)
    print("da_avg = %s" % da_avg)
    print("da_stdev = %s" % da_stdev)

    print(campaigns)

    # go through each campaign and award points on each stat based on how it compares to the mean and stdev

    for k, v in campaigns.items():
        print(k, v)
        # point amounts for above average (aa), average (a), and below average (ba)
        aa = Decimal(4/factor)
        a = Decimal(2/factor)
        ba = Decimal(1/factor)
        # multipliers for comments (cm), donation count (dcm), and donation amount (dam)
        cm = Decimal(1)
        dcm = Decimal(4.5)
        dam = Decimal(1)
        print("c_avg type = %s; c_stdev type = %s; v['comments'] type = %s" % (type(c_avg), type(c_stdev), type(v['comments'])))
        print("testing to see if 'comments' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['comments'], c_stdev, c_avg))
        # if this campaign's comments are within 1 standard deviation of the mean
        if (c_avg - c_stdev) <= v['comments'] <= (c_avg + c_stdev):
            # average * comments multiplier
            v['points'] += (a * cm)
            print("AVERAGE... awarded %s points" % (a * cm))
        # if this campaign's comments are above 1 standard deviation of the mean
        elif v['comments'] > (c_avg + c_stdev):
            # above average * comments multiplier
            v['points'] += (aa * cm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * cm))
        # if this campaign's comments are below 1 standard deviation of the mean
        elif v['comments'] < (c_avg - c_stdev):
            # below average * comments multiplier
            v['points'] += (ba * cm)
            print("BELOW AVERAGE... awarded %s point" % (ba * cm))

        print("testing to see if 'donation_count' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_count'], dc_stdev, dc_avg))
        # if this campaign's donation count is within 1 standard deviation of the mean
        if (dc_avg - dc_stdev) <= v['donation_count'] <= (dc_avg + dc_stdev):
            # average * donation count multiplier
            v['points'] += (a * dcm)
            print("AVERAGE... awarded %s points" % (a * dcm))
        # if this campaign's donation count is above 1 standard deviation of the mean
        elif v['donation_count'] > (dc_avg + dc_stdev):
            # above average * donation count multiplier
            v['points'] += (aa * dcm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * dcm))
        # if this campaign's donation count is below 1 standard deviation of the mean
        elif v['donation_count'] < (dc_avg - dc_stdev):
            # below average * donation count multiplier
            v['points'] += (ba * dcm)
            print("BELOW AVERAGE... awarded %s point" % (ba * dcm))

        print("testing to see if 'donation_amount' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_amount'], da_stdev, da_avg))
        # if this campaign's donation amount is within 1 standard deviation of the mean
        if (da_avg - da_stdev) <= v['donation_amount'] <= (da_avg + da_stdev):
            # average * donation amount multiplier
            v['points'] += (a * dam)
            print("AVERAGE... awarded %s points" % (a * dam))
        # if this campaign's donation amount is above 1 standard deviation of the mean
        elif v['donation_amount'] > (da_avg + da_stdev):
            # above average * donation amount multiplier
            v['points'] += (aa * dam)
            print("ABOVE AVERAGE... awarded %s points" % (aa * dam))
        # if this campaign's donation amount is below 1 standard deviation of the mean
        elif v['donation_amount'] < (da_avg - da_stdev):
            # below average * donation amount multiplier
            v['points'] += (ba * dam)
            print("BELOW AVERAGE... awarded %s point" % (ba * dam))

        # update the trending score in the database
        query = "update campaign_campaign set trending_score = '%s' where id = '%s';" % (v['points'], k)
        print(query)
        cur.execute(query)

        print("*" * 20)

        # debugging
        campaigns = OrderedDict(sorted(campaigns.items(), key=lambda t: t[1]['points'], reverse=True))
        for k, v in campaigns.items():
            print("campaign %s; points: %s; comments: %s; donation count: %s; donation amount: %s" % (k, v["points"], v["comments"], v["donation_count"], v["donation_amount"]))


if __name__ == "__main__":
    # connect to the database
    try:
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (config.settings["db_name"], config.settings["db_user"], config.settings["db_host"], config.settings["db_password"]))
        conn.autocommit = True
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    # get all the active campaigns
    query = "select id from campaign_campaign where is_active = 't' and deleted = 'f';"
    cur.execute(query)
    rows = cur.fetchall()
    for r in rows:
        print(r)

    # create a list of the campaigns ids
    campaign_ids = [p[0] for p in rows]
    print(campaign_ids)
    # find the trending scores for the campaigns
    trending(cur, campaign_ids, 10, 1, False)

    # find ties, then break ties
    ties = find_ties(cur)
    break_ties(cur, ties)

    conn.close()
