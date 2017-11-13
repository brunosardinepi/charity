from django.contrib import admin

from . import models


class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'upvotes', 'downvotes',)
    ordering = list_display

admin.site.register(models.FAQ, FAQAdmin)
