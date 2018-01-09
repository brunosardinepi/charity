from django.shortcuts import render
from django.views import View

from .models import Comment


class CommentPost(View):
    def get(self, request):
        c = request.GET.get('c')
        if c:
            comment = Comment.objects.get(pk=c)
            if comment:
#                obj = comment.content_object
#                if obj.get_model() == "Page":
                if comment.content_type == "page":
                    return HttpResponseRedirect("/{}/#c{}".format(obj.page_slug, comment.pk))
                elif comment.content_type == "campaign":
                    return HttpResponseRedirect("/{}/{}/{}/#c{}".format(
                        obj.page.page_slug,
                        obj.pk,
                        obj.campaign_slug,
                        comment.pk,
                    ))
