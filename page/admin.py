from django.contrib import admin

from . import models


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'page_slug',)
    ordering = ('id', 'name', 'page_slug',)
    filter_horizontal = ('admins',)

admin.site.register(models.Page, PageAdmin)
