from django.shortcuts import get_object_or_404, render

from . import models


def page(request, page_pk):
    page = get_object_or_404(models.Page, pk=page_pk)
    return render(request, 'page/page.html', {'page': page})
