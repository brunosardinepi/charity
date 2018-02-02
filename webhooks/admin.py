from django.contrib import admin

from . import models


class WebhookAdmin(admin.ModelAdmin):
    list_display = ('pk', 'event_id', 'object', 'created', 'type',)
    ordering = list_display
    list_filter = ('object', 'type',)

admin.site.register(models.Webhook, WebhookAdmin)
