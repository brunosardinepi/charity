from django.contrib import admin

from . import models


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'page', 'campaign', 'deleted',)
    ordering = list_display
    list_filter = ('user', 'deleted',)

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'comment', 'deleted',)
    ordering = list_display
    list_filter = ('user', 'deleted',)

admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Reply, ReplyAdmin)
