from django.contrib import admin

from . import models


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'date',)
    ordering = ('pk', 'user', 'date',)
    list_filter = ('user',)

admin.site.register(models.Error, ErrorAdmin)
