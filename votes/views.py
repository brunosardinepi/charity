import json

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Vote
from comments.models import Comment, Reply
from faqs.models import FAQ


class VoteView(View):
    def post(self, request):
        obj_original = request.POST.get('obj')
        obj = obj_original.split("-")[0]
        pk = obj_original.split("-")[1]

        vote_original = request.POST.get('vote')
        vote_original = vote_original.split(" ")[1]
        if vote_original == 'upvote':
            score = 1
        elif vote_original == 'downvote':
            score = -1

        # check if a vote already exists on this object for this user
        if obj == 'comment':
            comment = get_object_or_404(Comment, pk=pk)
            existing_vote = Vote.objects.filter(user=request.user, comment=comment)
            type = 'c'
        elif obj == 'reply':
            reply = get_object_or_404(Reply, pk=pk)
            existing_vote = Vote.objects.filter(user=request.user, reply=reply)
            type = 'r'
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
        elif obj == 'reply':
            vote = Vote.objects.create(
                user=request.user,
                score=score,
                reply=reply,
            )
            upvotes = reply.upvotes()
            downvotes = reply.downvotes()
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
            'vote': vote_original,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
