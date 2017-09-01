from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from . import models


class CampaignAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'campaign_slug', 'page',)
    ordering = ('id', 'name', 'campaign_slug', 'page',)
    list_filter = ('page',)
    filter_horizontal = ('campaign_admins', 'campaign_managers',)

admin.site.register(models.Campaign, CampaignAdmin)
