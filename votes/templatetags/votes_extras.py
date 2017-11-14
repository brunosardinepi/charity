from django import template
from django.shortcuts import get_object_or_404

from votes.models import Vote


register = template.Library()

@register.simple_tag
def user_vote_was(user, obj, pk):
    if obj == 'faq':
        vote = get_object_or_404(Vote, faq=pk, user=user)
    elif obj == 'comment':
        vote = get_object_or_404(Vote, comment=pk, user=user)
    if vote.score == 1:
        return "upvote"
    elif vote.score == -1:
        return "downvote"
