# PageFund

### Prerequisites

```
pagefund/config.py
```

```
pip install -r requirements.txt
```

```
crontab -e
0 2 * * * /bin/bash /home/[user]/pagefund/scripts/expire.sh
0 * * * * /home/[user]/pagefund/pagefundenv/bin/python3 /home/[user]/pagefund/pagefund/trending_pages.py
0 * * * * /home/[user]/pagefund/pagefundenv/bin/python3 /home/[user]/pagefund/pagefund/trending_campaigns.py
* * * * * /home/[user]/pagefund/pagefundenv/bin/python3 /home/[user]/pagefund/manage.py campaign_end
```

&copy; 2017 PageFund, Inc.
