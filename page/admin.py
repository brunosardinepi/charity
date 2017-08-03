from django.contrib import admin

from . import models


class PageAdmin(admin.ModelAdmin):
  list_display = ('id', 'name',)
  ordering = ('name',)

admin.site.register(models.Page, PageAdmin)
