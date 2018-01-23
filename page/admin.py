from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from . import models


class PageAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'trending_score', 'page_slug', 'category', 'deleted',)
    ordering = ('id', 'name', 'trending_score', 'page_slug',)
    list_filter = ('category', 'deleted',)
    filter_horizontal = ('admins', 'managers',)

class PageImageAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'page', 'caption', 'profile_picture', 'uploaded_at',)
    ordering = ('page', 'uploaded_at',)
    list_filter = ('page', 'profile_picture',)

admin.site.register(models.Page, PageAdmin)
admin.site.register(models.PageImage, PageImageAdmin)
