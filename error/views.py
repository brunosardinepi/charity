from django.shortcuts import render


def error_image_size(request):
    return render(request, 'error/error_image_size.html')
