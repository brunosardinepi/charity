from django.shortcuts import get_object_or_404, render

from .models import Note


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
