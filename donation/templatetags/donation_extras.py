from django import template

register = template.Library()

@register.filter(name='cents_to_dollars')
def cents_to_dollars(n):
    if n is None:
        return "$0"
    else:
        return "$%s" % int(n / 100)

@register.filter(name='progress_width')
def progress_width(campaign):
    if campaign.donation_money() == 0:
        return 0
    else:
        return int((campaign.donation_money() / (campaign.goal * 100)) * 100)

@register.filter(name='progress_value')
def progress_value(m):
    if m == 0:
        return 0
    else:
        return int(m / 100)
