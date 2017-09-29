from django.shortcuts import render


def error_forgotpasswordreset_expired(request):
    return render(request, 'error/error_forgotpasswordreset_expired.html')

def error_forgotpasswordreset_completed(request):
    return render(request, 'error/error_forgotpasswordreset_completed.html')

def error_image_size(request):
    return render(request, 'error/error_image_size.html')

def error_invite_user_exists(request):
    return render(request, 'error/error_invite_user_exists.html')