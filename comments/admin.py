from django.contrib import admin

from . import models


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'content_type', 'comment', 'deleted',)
    ordering = list_display
    list_filter = ('user', 'content_type', 'deleted',)

admin.site.register(models.Comment, CommentAdmin)
