from django.shortcuts import render


def error_image_size(request):
    return render(request, 'error/error_image_size.html')

def error_invite_user_exists(request):
    return render(request, 'error/error_invite_user_exists.html')
