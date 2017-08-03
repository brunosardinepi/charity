from django.shortcuts import get_object_or_404, render

from . import models


def page(request, slug):
    page = get_object_or_404(models.Page, slug=slug)
    return render(request, 'page/page.html', {'page': page})
