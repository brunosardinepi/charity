from django.contrib import admin

from . import models


class NoteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'date', 'type',)
    ordering = ('pk', 'user', 'date', 'type',)
    list_filter = ('user', 'type',)

admin.site.register(models.Note, NoteAdmin)
