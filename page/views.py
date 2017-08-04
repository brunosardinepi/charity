from django.shortcuts import get_object_or_404, render

from . import models


def page(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    return render(request, 'page/page.html', {'page': page})
