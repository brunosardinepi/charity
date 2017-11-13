#!/home/gnowak/pagefund/pagefundenv/bin/python3

from decimal import Decimal
from collections import Counter, OrderedDict
import config
import psycopg2
import statistics


def trim(l, p):
    x = list(l)
    p /= 100
    print("list = %s" % x)
    print("percentage = %s" % p)
    print("the mean of the original list is: %s" % statistics.mean(x))
    # find number of items in x
    c = len(x)
    print("there are %s items in the list" % c)
    if c > 3:
        r = int(c * p)
        if r > 0:
            print("we'll remove %s items from the front and back" % r)
            # re-order x from big to small
            x.sort()
            print("sorted list = %s" % x)
            # remove 10% of items from the front
            del x[:r]
            print("removed %s items from the front and got: %s" % (r, x))
            # remove 10% of items from the back
            del x[-r:]
            print("removed %s items from the back and got: %s" % (r, x))
    return x

def trimmed_mean(l, p):
    x = trim(l, p)
    print("the mean of the new list is: %s" % statistics.mean(x))
    return int(statistics.mean(x))

def trimmed_stdev(l, p):
    x = trim(l, p)
    print("the stdev of the new list is: %s" % statistics.pstdev(x))
    return int(statistics.pstdev(x))

def find_ties(cur):
    # sort by trending score from highest to lowest
    scores = []

#    # debugging only. delete after
#    query = "update page_page set trending_score = {} where id = {};".format(40.0, 29)
#    cur.execute(query)

    # get a list of the duplicate trending scores
    query = "select trending_score from campaign_campaign order by trending_score desc;"
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
    # find the comments, subscriptions, donation_count, and donation_amount for each campaign and put them in their own list
    comments, subscriptions, donation_count, donation_amount = [], [], [], []
    campaigns = {}
    for p in campaign_ids:
        query = "select count(*) from comments_comment where campaign_id = '%s' and deleted = 'f';" % p
        cur.execute(query)
        c = cur.fetchall()
        c = c[0][0]
        if c is None:
            c = 0
        comments.append(c)
        print("c = %s" % c)

#        query = "select count(*) from page_page_subscribers where page_id = '%s';" % p
#        cur.execute(query)
#        s = cur.fetchall()
#        s = s[0][0]
#        if s is None:
#            s = 0
#        subscriptions.append(s)
#        print("s = %s" % s)

        query = "select count(*) from donation_donation where campaign_id = '%s';" % p
        cur.execute(query)
        dc = cur.fetchall()
        dc = dc[0][0]
        if dc is None:
            dc = 0
        donation_count.append(dc)
        print("dc = %s" % dc)

        query = "select sum(amount) from donation_donation where campaign_id = '%s';" % p
        cur.execute(query)
        da = cur.fetchall()
        da = da[0][0]
        if da is None:
            da = 0
        donation_amount.append(da)
        print("da = %s" % da)

        # store in a dict for access later
        campaigns[p] = {
            'comments': c,
            'donation_count': dc,
            'donation_amount': da,
#            'points': 0,
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
#    s_avg, s_stdev = trimmed_mean(subscriptions, 10), trimmed_stdev(subscriptions, 10)
#    print("s_avg = %s" % s_avg)
#    print("s_stdev = %s" % s_stdev)
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
        if (c_avg - c_stdev) <= v['comments'] <= (c_avg + c_stdev):
            v['points'] += (a * cm)
            print("AVERAGE... awarded %s points" % (a * cm))
        elif v['comments'] > (c_avg + c_stdev):
            v['points'] += (aa * cm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * cm))
        elif v['comments'] < (c_avg - c_stdev):
            v['points'] += (ba * cm)
            print("BELOW AVERAGE... awarded %s point" % (ba * cm))

#        print("testing to see if 'subscriptions' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['subscriptions'], s_stdev, s_avg))
#        if (s_avg - s_stdev) <= v['subscriptions'] <= (s_avg + s_stdev):
#            v['points'] += (a * sm)
#            print("AVERAGE... awarded %s points" % (a * sm))
#        elif v['subscriptions'] > (s_avg + s_stdev):
#            v['points'] += (aa * sm)
#            print("ABOVE AVERAGE... awarded %s points" % (aa * sm))
#        elif v['subscriptions'] < (s_avg - s_stdev):
#            v['points'] += (ba * sm)
#            print("BELOW AVERAGE... awarded %s points" % (ba * sm))

        print("testing to see if 'donation_count' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_count'], dc_stdev, dc_avg))
        if (dc_avg - dc_stdev) <= v['donation_count'] <= (dc_avg + dc_stdev):
            v['points'] += (a * dcm)
            print("AVERAGE... awarded %s points" % (a * dcm))
        elif v['donation_count'] > (dc_avg + dc_stdev):
            v['points'] += (aa * dcm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * dcm))
        elif v['donation_count'] < (dc_avg - dc_stdev):
            v['points'] += (ba * dcm)
            print("BELOW AVERAGE... awarded %s point" % (ba * dcm))

        print("testing to see if 'donation_amount' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_amount'], da_stdev, da_avg))
        if (da_avg - da_stdev) <= v['donation_amount'] <= (da_avg + da_stdev):
            v['points'] += (a * dam)
            print("AVERAGE... awarded %s points" % (a * dam))
        elif v['donation_amount'] > (da_avg + da_stdev):
            v['points'] += (aa * dam)
            print("ABOVE AVERAGE... awarded %s points" % (aa * dam))
        elif v['donation_amount'] < (da_avg - da_stdev):
            v['points'] += (ba * dam)
            print("BELOW AVERAGE... awarded %s point" % (ba * dam))

        query = "update campaign_campaign set trending_score = '%s' where id = '%s';" % (v['points'], k)
        print(query)
        cur.execute(query)

        print("*" * 20)

        # debugging
        campaigns = OrderedDict(sorted(campaigns.items(), key=lambda t: t[1]['points'], reverse=True))
        for k, v in campaigns.items():
            print("campaign %s; points: %s; comments: %s; donation count: %s; donation amount: %s" % (k, v["points"], v["comments"], v["donation_count"], v["donation_amount"]))


if __name__ == "__main__":
    try:
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (config.settings["db_name"], config.settings["db_user"], config.settings["db_host"], config.settings["db_password"]))
        conn.autocommit = True
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    query = "select id from campaign_campaign where is_active = 't';"
    cur.execute(query)
    rows = cur.fetchall()
    for r in rows:
        print(r)

    campaign_ids = [p[0] for p in rows]
    print(campaign_ids)
    trending(cur, campaign_ids, 10, 1, False)

    # find ties, then break ties
    ties = find_ties(cur)
    break_ties(cur, ties)

    conn.close()
