import json

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Vote
from comments.models import Comment
from faqs.models import FAQ


class VoteView(View):
    def post(self, request):
        obj_original = request.POST.get('obj')
        obj = obj_original.split("-")[0]
        pk = obj_original.split("-")[1]

        score = request.POST.get('vote')
        score = score.split(" ")[1]
        if score == 'upvote':
            score = 1
        elif score == 'downvote':
            score = -1

        # check if a vote already exists on this object for this user
        if obj == 'comment':
            comment = get_object_or_404(Comment, pk=pk)
            existing_vote = Vote.objects.filter(user=request.user, comment=comment)
            type = 'c'
        elif obj == 'faq':
            faq = get_object_or_404(FAQ, pk=pk)
            existing_vote = Vote.objects.filter(user=request.user, faq=faq)
            type = 'f'

        if len(existing_vote) > 0:
            # vote already exists, so delete it
            existing_vote.delete()
        # create a vote for this user
        if obj == 'comment':
            vote = Vote.objects.create(
                user=request.user,
                score=score,
                comment=comment,
            )
            upvotes = comment.upvotes()
            downvotes = comment.downvotes()
        elif obj == 'faq':
            vote = Vote.objects.create(
                user=request.user,
                score=score,
                faq=faq,
            )
            upvotes = faq.upvotes()
            downvotes = faq.downvotes()
        data = {
            'pk': pk,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'type': type,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
