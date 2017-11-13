#!/home/gnowak/pagefund/pagefundenv/bin/python3

import collections
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

def find_ties(page_ids):
    # sort by trending score from highest to lowest
    # compare the current page's trending score to the next page's trending score
    # if it's different, move on and do it again for the next page until we reach the end
    # if it's the same, put both of these into their own dictionary with the score as the key and the page ids as the value,
    # then check the next page to see if it's the same, and repeat until it's different
    # return a dictionary of ties

def break_ties(cur, page_ids):
    # go through each key in the page_ids dictionary
    # run the pages through the trending function, but divide the points by 10 to make them a decimal,
    # and add them to the current trending score instead of replacing it

def trending(cur, page_ids, trim_pct):
    # find the comments, subscriptions, donation_count, and donation_amount for each page and put them in their own list
    # initialize the lists we need for storing data later
    comments, subscriptions, donation_count, donation_amount = [], [], [], []
    pages = {}
    # do for each page
    for p in page_ids:
        # find the number of comments for the page
        query = "select count(*) from comments_comment where page_id = '%s' and deleted = 'f';" % p
        cur.execute(query)
        c = cur.fetchall()
        c = c[0][0]
        if c is None:
            c = 0
        # append to the comments list
        comments.append(c)
        print("c = %s" % c)

        # find the number of subscribers for the page
        query = "select count(*) from page_page_subscribers where page_id = '%s';" % p
        cur.execute(query)
        s = cur.fetchall()
        s = s[0][0]
        if s is None:
            s = 0
        # append to the subscriptions list
        subscriptions.append(s)
        print("s = %s" % s)

        # find the number of donations for the page
        query = "select count(*) from donation_donation where page_id = '%s';" % p
        cur.execute(query)
        dc = cur.fetchall()
        dc = dc[0][0]
        if dc is None:
            dc = 0
        # append to the donation list
        donation_count.append(dc)
        print("dc = %s" % dc)

        # find the total amount of the donations for the page
        query = "select sum(amount) from donation_donation where page_id = '%s';" % p
        cur.execute(query)
        da = cur.fetchall()
        da = da[0][0]
        if da is None:
            da = 0
        # append to the donation amount list
        donation_amount.append(da)
        print("da = %s" % da)

        # store in a dict for access later
        pages[p] = {
            'comments': c,
            'subscriptions': s,
            'donation_count': dc,
            'donation_amount': da,
            'points': 0
        }

    # once all the stats have been added to their own lists, find the trimmed mean and trimmed stdev for each stat
    c_avg, c_stdev = trimmed_mean(comments, trim_pct), trimmed_stdev(comments, trim_pct)
    print("c_avg = %s" % c_avg)
    print("c_stdev = %s" % c_stdev)
    s_avg, s_stdev = trimmed_mean(subscriptions, trim_pct), trimmed_stdev(subscriptions, trim_pct)
    print("s_avg = %s" % s_avg)
    print("s_stdev = %s" % s_stdev)
    dc_avg, dc_stdev = trimmed_mean(donation_count, trim_pct), trimmed_stdev(donation_count, trim_pct)
    print("dc_avg = %s" % dc_avg)
    print("dc_stdev = %s" % dc_stdev)
    da_avg, da_stdev = trimmed_mean(donation_amount, trim_pct), trimmed_stdev(donation_amount, trim_pct)
    print("da_avg = %s" % da_avg)
    print("da_stdev = %s" % da_stdev)

    print(pages)

    # go through each page and award points on each stat based on how it compares to the mean and stdev
    for k, v in pages.items():
        print(k, v)
        # point amounts for above average (aa), average (a), and below average (ba)
        aa, a, ba = 4, 2, 1
        # multipliers for comments (cm), subscriptions (sm), donation count (dcm), and donation amount (dam)
        cm, sm, dcm, dam = 1, 4, 4.5, 1
        print("c_avg type = %s; c_stdev type = %s; v['comments'] type = %s" % (type(c_avg), type(c_stdev), type(v['comments'])))
        print("testing to see if 'comments' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['comments'], c_stdev, c_avg))
        # if this page's comments are within 1 standard deviation of the mean
        if (c_avg - c_stdev) <= v['comments'] <= (c_avg + c_stdev):
            # average * comments multiplier
            v['points'] += (a * cm)
            print("AVERAGE... awarded %s points" % (a * cm))
        # if this page's comments are above 1 standard deviation of the mean
        elif v['comments'] > (c_avg + c_stdev):
            # above average * comments multiplier
            v['points'] += (aa * cm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * cm))
        # if this page's comments are below 1 standard deviation of the mean
        elif v['comments'] < (c_avg - c_stdev):
            # below average * comments multiplier
            v['points'] += (ba * cm)
            print("BELOW AVERAGE... awarded %s point" % (ba * cm))

        print("testing to see if 'subscriptions' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['subscriptions'], s_stdev, s_avg))
        # if this page's subscriptions are within 1 standard deviation of the mean
        if (s_avg - s_stdev) <= v['subscriptions'] <= (s_avg + s_stdev):
            # average * subscriptions multiplier
            v['points'] += (a * sm)
            print("AVERAGE... awarded %s points" % (a * sm))
        # if this page's subscriptions are above 1 standard deviation of the mean
        elif v['subscriptions'] > (s_avg + s_stdev):
            # above average * subscriptions multiplier
            v['points'] += (aa * sm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * sm))
        # if this page's subscriptions are below 1 standard deviation of the mean
        elif v['subscriptions'] < (s_avg - s_stdev):
            # below average * subscriptions multiplier
            v['points'] += (ba * sm)
            print("BELOW AVERAGE... awarded %s points" % (ba * sm))

        print("testing to see if 'donation_count' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_count'], dc_stdev, dc_avg))
        # if this page's donation count is within 1 standard deviation of the mean
        if (dc_avg - dc_stdev) <= v['donation_count'] <= (dc_avg + dc_stdev):
            # average * donation count multiplier
            v['points'] += (a * dcm)
            print("AVERAGE... awarded %s points" % (a * dcm))
        # if this page's donation count is above 1 standard deviation of the mean
        elif v['donation_count'] > (dc_avg + dc_stdev):
            # above average * donation count multiplier
            v['points'] += (aa * dcm)
            print("ABOVE AVERAGE... awarded %s points" % (aa * dcm))
        # if this page's donation count is below 1 standard deviation of the mean
        elif v['donation_count'] < (dc_avg - dc_stdev):
            # below average * donation count multiplier
            v['points'] += (ba * dcm)
            print("BELOW AVERAGE... awarded %s point" % (ba * dcm))

        print("testing to see if 'donation_amount' (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_amount'], da_stdev, da_avg))
        # if this page's donation amount is within 1 standard deviation of the mean
        if (da_avg - da_stdev) <= v['donation_amount'] <= (da_avg + da_stdev):
            # average * donation amount multiplier
            v['points'] += (a * dam)
            print("AVERAGE... awarded %s points" % (a * dam))
        # if this page's donation amount is above 1 standard deviation of the mean
        elif v['donation_amount'] > (da_avg + da_stdev):
            # above average * donation amount multiplier
            v['points'] += (aa * dam)
            print("ABOVE AVERAGE... awarded %s points" % (aa * dam))
        # if this page's donation amount is below 1 standard deviation of the mean
        elif v['donation_amount'] < (da_avg - da_stdev):
            # below average * donation amount multiplier
            v['points'] += (ba * dam)
            print("BELOW AVERAGE... awarded %s point" % (ba * dam))

        # update the trending score in the database
        query = "update page_page set trending_score = '%s' where id = '%s';" % (v['points'], k)
        print(query)
        cur.execute(query)

        print("*" * 20)

    # debugging
    pages = collections.OrderedDict(sorted(pages.items(), key=lambda t: t[1]['points'], reverse=True))
    for k, v in pages.items():
        print("page %s; points: %s; comments: %s; subscriptions: %s; donation count: %s; donation amount: %s" % (k, v["points"], v["comments"], v["subscriptions"], v["donation_count"], v["donation_amount"]))


if __name__ == "__main__":
    # connect to the database
    try:
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (config.settings["db_name"], config.settings["db_user"], config.settings["db_host"], config.settings["db_password"]))
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    # get all the pages
    query = "select id from page_page"
    cur.execute(query)
    rows = cur.fetchall()
    for r in rows:
        print(r)

    # create a list of the page ids
    page_ids = [p[0] for p in rows]
    print(page_ids)
    # find the trending scores for the pages
    trending(cur, page_ids, 10)
    # commit the database changes
    conn.commit()
    # close the database connection
    conn.close()
