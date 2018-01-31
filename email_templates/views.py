from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import EmailTemplate


class EmailList(View):
    def get(self, request):
        authorized_users = [
            'gn9012@gmail.com',
            'dustin@page.fund',
            'mona@page.fund',
        ]
        if request.user.email in authorized_users:
            email_templates = EmailTemplate.objects.all().order_by('name')
            return render(request, 'email_templates/email_list.html', {'email_templates': email_templates})
        else:
            raise Http404

class EmailDetail(View):
    def get(self, request, email_pk):
        email_template = get_object_or_404(EmailTemplate, pk=email_pk)
        return render(request, 'email_templates/email_detail.html', {'email_template': email_template})
