from django import template
from django.shortcuts import get_object_or_404

from votes.models import Vote


register = template.Library()

@register.simple_tag
def user_vote_was(user, obj, pk):
    if obj == 'faq':
        try:
            vote = Vote.objects.get(faq=pk, user=user)
        except Vote.DoesNotExist:
            vote = None
    elif obj == 'comment':
        try:
            vote = Vote.objects.get(comment=pk, user=user)
        except Vote.DoesNotExist:
            vote = None
    elif obj == 'reply':
        try:
            vote = Vote.objects.get(reply=pk, user=user)
        except Vote.DoesNotExist:
            vote = None
    if vote is not None:
        if vote.score == 1:
            return "upvote"
        elif vote.score == -1:
            return "downvote"
    else:
        return None
