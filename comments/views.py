from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .forms import CommentForm
from .models import Comment
from pagefund.utils import get_content_type


class CommentPost(View):
    def post(self, request, content_type, object_id):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content_type = get_content_type(content_type)
            comment.object_id = object_id
            comment.save()
            return HttpResponseRedirect(comment.content_object.get_absolute_url() + "#c{}".format(comment.pk))
