#####
# Calculating the trending pages
#
# High-level steps:
# 1. Find the trimmed mean of each Page quality across all Pages
# 2. Find the standard deviation of each Page quality across all Pages
# 3. Evaluate each Page's qualities.
#     a. If a quality is above the mean + standard deviation, it is above average.
#     b. If a quality is within the mean +/- standard deviation, it is average.
#     c. If a quality is below the mean - standard deviation, it is below average.
# 4. Award points for each Page quality based on how it compares to the mean.
#     a. Above average = 4 points
#     b. Average = 2 points
#     c. Below average = 1 point
# 5. Sum each Page's quality points and then order them from highest to lowest. The highest scoring pages are "trending".
#####

from trending_pages import create_pages
from collections import OrderedDict

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
#    print("the stdev of the new list is: %s" % statistics.pstdev(x))
    return int(statistics.pstdev(x))

def trending(file):
    # scrape the file we are using for testing so that we can find the mean and standard deviation
    with open(file) as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        # separate the qualities into their own lists
        comments, subscriptions, donation_count, donation_amount = [], [], [], []
        pages = {}
        for l in lines:
            if l[0] == "#":
                continue
            p = l.split("page:")[1]
            p = p.split(";")[0]

            c = l.split("comments:")[1]
            c = int(c.split(";")[0])
            comments.append(c)

            s = l.split("subscriptions:")[1]
            s = int(s.split(";")[0])
            subscriptions.append(s)

            dc = l.split("count:")[1]
            dc = int(dc.split(";")[0])
            donation_count.append(dc)

            da = l.split("amount:")[1]
            da = int(da.split(";")[0])
            donation_amount.append(da)

            pages[p] = {
                'comments': c,
                'subscriptions': s,
                'donation_count': dc,
                'donation_amount': da,
                'points': 0
            }
#        print("comments --- avg: %s --- stdev: %s --- list: %s" % (trimmed_mean(comments, 10), trimmed_stdev(comments, 10), comments))
#        print("subscriptions --- avg: %s --- stdev: %s --- list: %s" % (trimmed_mean(subscriptions, 10), trimmed_stdev(subscriptions, 10), subscriptions))
#        print("donation_count --- avg: %s --- stdev: %s --- list: %s" % (trimmed_mean(donation_count, 10), trimmed_stdev(donation_count, 10), donation_count))
#        print("donation_amount --- avg: %s --- stdev: %s --- list: %s" % (trimmed_mean(donation_amount, 10), trimmed_stdev(donation_amount, 10), donation_amount))
        print("pages = %s" % pages)

        c_avg, c_stdev = trimmed_mean(comments, 10), trimmed_stdev(comments, 10)
#        print("c_avg = %s" % c_avg)
#        print("c_stdev = %s" % c_stdev)
        s_avg, s_stdev = trimmed_mean(subscriptions, 10), trimmed_stdev(subscriptions, 10)
#        print("s_avg = %s" % s_avg)
#        print("s_stdev = %s" % s_stdev)
        dc_avg, dc_stdev = trimmed_mean(donation_count, 10), trimmed_stdev(donation_count, 10)
#        print("dc_avg = %s" % dc_avg)
#        print("dc_stdev = %s" % dc_stdev)
        da_avg, da_stdev = trimmed_mean(donation_amount, 10), trimmed_stdev(donation_amount, 10)
#        print("da_avg = %s" % da_avg)
#        print("da_stdev = %s" % da_stdev)

        for k, v in pages.items():
            print(k, v)
            aa, a, ba = 4, 2, 1
#            print("c_avg type = %s; c_stdev type = %s; v['comments'] type = %s" % (type(c_avg), type(c_stdev), type(v['comments'])))
            print("testing to see if v['comments'] (%s) is within 1 stdev (%s) of the mean (%s)" % (v['comments'], c_stdev, c_avg))
            if (c_avg - c_stdev) <= v['comments'] <= (c_avg + c_stdev):
                print("average")
                v['points'] += a
                print("awarded %s points" % a)
            elif v['comments'] > (c_avg + c_stdev):
                print("above average")
                v['points'] += aa
                print("awarded %s points" % aa)
            elif v['comments'] < (c_avg - c_stdev):
                print("below average")
                v['points'] += ba
                print("awarded %s point" % ba)

            print("testing to see if v['subscriptions'] (%s) is within 1 stdev (%s) of the mean (%s)" % (v['subscriptions'], s_stdev, s_avg))
            if (s_avg - s_stdev) <= v['subscriptions'] <= (s_avg + s_stdev):
                print("average")
                v['points'] += (a * 2)
                print("awarded %s points" % (a * 2))
            elif v['subscriptions'] > (s_avg + s_stdev):
                print("above average")
                v['points'] += (aa * 2)
                print("awarded %s points" % (aa * 2))
            elif v['subscriptions'] < (s_avg - s_stdev):
                print("below average")
                v['points'] += (ba * 2)
                print("awarded %s point" % (ba * 2))

            print("testing to see if v['donation_count'] (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_count'], dc_stdev, dc_avg))
            if (dc_avg - dc_stdev) <= v['donation_count'] <= (dc_avg + dc_stdev):
                print("average")
                v['points'] += (a * 4)
                print("awarded %s points" % (a * 4))
            elif v['donation_count'] > (dc_avg + dc_stdev):
                print("above average")
                v['points'] += (aa * 4)
                print("awarded %s points" % (aa * 4))
            elif v['donation_count'] < (dc_avg - dc_stdev):
                print("below average")
                v['points'] += (ba * 4)
                print("awarded %s point" % (ba * 4))

            print("testing to see if v['donation_amount'] (%s) is within 1 stdev (%s) of the mean (%s)" % (v['donation_amount'], da_stdev, da_avg))
            if (da_avg - da_stdev) <= v['donation_amount'] <= (da_avg + da_stdev):
                print("average")
                v['points'] += a
                print("awarded %s points" % a)
            elif v['donation_amount'] > (da_avg + da_stdev):
                print("above average")
                v['points'] += aa
                print("awarded %s points" % aa)
            elif v['donation_amount'] < (da_avg - da_stdev):
                print("below average")
                v['points'] += ba
                print("awarded %s point" % ba)

        print("pages before sort = %s" % pages)
        pages = OrderedDict(sorted(pages.items(), key=lambda t: t[1]['points'], reverse=True))
        print("pages after sort = %s" % pages)
        print("*" * 10)
        for k, v in pages.items():
            print(k, v)

if __name__ == "__main__":
    create_pages(10)
    trending("/home/gnowak/pagefund/scripts/trending.txt")
