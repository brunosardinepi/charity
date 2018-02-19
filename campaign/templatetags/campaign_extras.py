from django import template
from django.utils import timezone


register = template.Library()

@register.filter
def in_the_future(value):
    return value > timezone.now()