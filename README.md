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
0 2 * * * /bin/bash /home/gnowak/pagefund/scripts/expire.sh
0 * * * * /home/gnowak/pagefund/pagefundenv/bin/python3 /home/gnowak/pagefund/pagefund/trending_pages.py
0 * * * * /home/gnowak/pagefund/pagefundenv/bin/python3 /home/gnowak/pagefund/pagefund/trending_campaigns.py
```

&copy; 2017 PageFund, Inc.
