from django.shortcuts import render
from django.views import View

from .models import FAQ


class FAQList(View):
    def get(self, request):
        faqs = FAQ.objects.filter(archived=False).order_by('order')
        return render(self.request, 'faqs/faq_list.html', {'faqs': faqs})
