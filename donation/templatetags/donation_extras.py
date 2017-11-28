from django import template

register = template.Library()

@register.filter(name='cents_to_dollars')
def cents_to_dollars(n):
    if n is None:
        return "$0"
    else:
        return "$%s" % int(n / 100)
