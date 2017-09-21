from django import template
from django.shortcuts import get_object_or_404

from comments import models


register = template.Library()

@register.simple_tag
def comment_replies(comment_pk):
    comment = get_object_or_404(models.Comment, pk=comment_pk)
    replies = models.Reply.objects.filter(comment=comment, deleted=False).order_by('date')
    return replies
