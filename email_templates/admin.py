from django.contrib import admin

from .models import EmailTemplate


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    ordering = list_display

admin.site.register(EmailTemplate, EmailTemplateAdmin)

