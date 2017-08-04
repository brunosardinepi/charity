from django.contrib import admin

from . import models


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'campaign_slug', 'page',)
    ordering = ('id', 'name', 'campaign_slug', 'page',)
    list_filter = ('page',)

admin.site.register(models.Campaign, CampaignAdmin)
