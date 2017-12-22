from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from . import forms
from .models import Note
from .utils import create_note
from comments.models import Comment, Reply


def error_forgotpasswordreset_expired(request):
    return render(request, 'notes/error_forgotpasswordreset_expired.html')

def error_forgotpasswordreset_completed(request):
    return render(request, 'notes/error_forgotpasswordreset_completed.html')

def error_image_size(request):
    return render(request, 'notes/error_image_size.html')

def error_invite_user_exists(request):
    return render(request, 'notes/error_invite_user_exists.html')

def error_image_type(request):
    return render(request, 'notes/error_image_type.html')

def error_amount_is_none(request):
    return render(request, 'notes/error_amount_is_none.html')

def error_stripe_invalid_request(request, error_pk):
    error = get_object_or_404(Note, pk=error_pk)
    msg = error.message
    msg = msg.split(": ", 1)[1]
    return render(request, 'notes/error_stripe_invalid_request.html', {
        'message': msg,
    })


class AbuseComment(View):
    def get_obj(self, type, obj_pk):
        if type == 'comment':
            obj = get_object_or_404(Comment, pk=obj_pk)
        elif type == 'reply':
            obj = get_object_or_404(Reply, pk=obj_pk)

        return obj

    def get(self, request, type, obj_pk):
        obj = self.get_obj(type, obj_pk)
        form = forms.AbuseCommentForm()
        return render(request, 'notes/abuse_comment.html', {
            'obj': obj,
            'form': form,
        })

    def post(self, request, type, obj_pk):
        obj = self.get_obj(type, obj_pk)
        form = forms.AbuseCommentForm(request.POST)
        if form.is_valid():
            create_note(request, obj, 'abuse')
        # idk where to redirect this to
        return redirect('home')


def error_stripe_invalid_request(request, error_pk):
    error = get_object_or_404(Note, pk=error_pk)
    msg = error.message
    msg = msg.split(": ", 1)[1]
    return render(request, 'notes/error_stripe_invalid_request.html', {
        'message': msg,
    })
