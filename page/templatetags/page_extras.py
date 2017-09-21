from django import template
from django.shortcuts import get_object_or_404

from page import models


register = template.Library()

@register.simple_tag
def active_campaigns(page_pk):
    page = get_object_or_404(models.Page, pk=page_pk)
    active_campaigns = page.campaigns.filter(is_active=True, deleted=False).order_by("name")
    return active_campaigns
