from django.contrib import admin

from . import models


class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'score', 'comment', 'faq',)
    ordering = list_display
    list_filter = ('user', 'comment', 'faq',)

admin.site.register(models.Vote, VoteAdmin)
