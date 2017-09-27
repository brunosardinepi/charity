from django import template

register = template.Library()

@register.filter(name='cents_to_dollars')
def cents_to_dollars(n):
    return "$%s" % int(n / 100)
