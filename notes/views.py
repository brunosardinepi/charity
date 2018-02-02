from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from . import forms
from .models import Note
from .utils import create_note
from campaign.models import CampaignImage
from comments.models import Comment
from page.models import PageImage


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

def error_campaign_vote_participants(request):
    previous_page = request.META.get('HTTP_REFERER')
    return render(request, 'notes/error_campaign_vote_participants.html', {
        'previous_page': previous_page,
    })

def error_page_does_not_exist(request):
    return render(request, 'notes/error_page_does_not_exist.html')

def error_campaign_does_not_exist(request):
    return render(request, 'notes/error_campaign_does_not_exist.html')

class AbuseComment(View):
    def get(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        form = forms.AbuseForm()
        return render(request, 'notes/abuse_comment.html', {
            'comment': comment,
            'form': form,
        })

    def post(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        form = forms.AbuseForm(request.POST)
        if form.is_valid():
            create_note(request, comment, 'abuse')
        # idk where to redirect this to. maybe a thank you page
        return redirect('home')


class AbuseImage(View):
    def get(self, request, type, image_pk):
        if type == "page":
            image = get_object_or_404(PageImage, pk=image_pk)
        elif type == "campaign":
            image = get_object_or_404(CampaignImage, pk=image_pk)
        form = forms.AbuseForm()
        return render(request, 'notes/abuse_image.html', {
            'image': image,
            'form': form,
        })

    def post(self, request, type, image_pk):
        if type == "page":
            image = get_object_or_404(PageImage, pk=image_pk)
        elif type == "campaign":
            image = get_object_or_404(CampaignImage, pk=image_pk)
        form = forms.AbuseForm(request.POST)
        if form.is_valid():
            create_note(request, image, 'abuse')
        # idk where to redirect this to. maybe a thank you page
        return redirect('home')


def error_stripe_invalid_request(request, error_pk):
    error = get_object_or_404(Note, pk=error_pk)
    msg = error.message
    msg = msg.split(": ", 1)[1]
    return render(request, 'notes/error_stripe_invalid_request.html', {
        'message': msg,
    })
