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
        # check if a vote already exists on this object for this user
        obj_original = request.POST.get('obj')
        obj = obj_original.split("-")[0]
        pk = obj_original.split("-")[1]

        score = request.POST.get('score')
        score = score.split("-")[1]
        if score == 'upvote':
            score = 1
        elif score == 'downvote':
            score = -1

        if obj == 'comment':
            comment = get_object_or_404(Comment, pk=pk)
            existing_vote = Vote.objects.filter(user=request.user, comment=comment)
        elif obj == 'faq':
            faq = get_object_or_404(FAQ, pk=pk)
            existing_vote = Vote.objects.filter(user=request.user, faq=faq)

        if len(existing_vote) > 0:
            # vote already exists, so delete it
            print("vote already exists, deleting it now")
            existing_vote.delete()
        # create a vote for this user
        if obj == 'comment':
            vote = Vote.objects.create(
                user=request.user,
                score=score,
                comment=comment,
            )
            current_score = Vote.objects.filter(comment=comment).aggregate(Sum('score')).get('score__sum')
        elif obj == 'faq':
            vote = Vote.objects.create(
                user=request.user,
                score=score,
                faq=faq,
            )
            current_score = Vote.objects.filter(faq=faq).aggregate(Sum('score')).get('score__sum')

        data = {
            'score': current_score,
            'pk': pk,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
