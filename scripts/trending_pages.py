import random


def create_pages(n):
    # page:a;comments:100;subscriptions:20;count:5;amount:100

    with open('/home/gnowak/pagefund/scripts/trending.txt', 'w') as f:
        for i in range(n):
            x = "page:%s;comments:%s;subscriptions:%s;count:%s;amount:%s\n" % (
                i,
                random.randint(1, 1000),
                random.randint(1, 1000),
                random.randint(1, 1000),
                random.randint(1, 100000)
            )
            f.write(x)

if __name__ == "__main__":
    create_pages(10)
