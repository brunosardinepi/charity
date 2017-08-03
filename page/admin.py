from django.contrib import admin

from . import models


class PageAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'slug',)
  ordering = ('id', 'name', 'slug',)

admin.site.register(models.Page, PageAdmin)
