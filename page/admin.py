from django.contrib import admin

from . import models


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'page_slug', 'category',)
    ordering = ('id', 'name', 'page_slug',)
    list_filter = ('category',)
    filter_horizontal = ('admins',)

admin.site.register(models.Page, PageAdmin)
