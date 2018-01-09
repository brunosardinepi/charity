from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .forms import CommentForm
from .models import Comment
from pagefund.utils import get_content_type


class CommentPost(View):
#    def get(self, request):
#        c = request.GET.get('c')
#        if c:
#            comment = Comment.objects.get(pk=c)
#            if comment:
#                if comment.content_type == "page":
#                    return HttpResponseRedirect("/{}/#c{}".format(obj.page_slug, comment.pk))
#                elif comment.content_type == "campaign":
#                    return HttpResponseRedirect("/{}/{}/{}/#c{}".format(
#                        obj.page.page_slug,
#                        obj.pk,
#                        obj.campaign_slug,
#                        comment.pk,
#                    ))
    def post(self, request, content_type, object_id):
        print("content_type = {}".format(content_type))
        print("content_type = {}".format(get_content_type(content_type)))
        print("object_id = {}".format(object_id))
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content_type = get_content_type(content_type)
            comment.object_id = object_id
            comment.save()
            return HttpResponseRedirect(comment.content_object.get_absolute_url())
        else:
            print(form.errors)
